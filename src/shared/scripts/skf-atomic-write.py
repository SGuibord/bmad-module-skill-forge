# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""SKF Atomic Write — Crash-safe artifact writing for skill workflows.

Provides three CLI subcommands skills can invoke via bash to avoid
partial-write corruption and active-symlink races.

Subcommands:
  write      Stage content into <target>.skf-tmp, fsync, then rename to <target>.
             Content comes from stdin. Creates parent dirs as needed.

  stage-dir  Create <target>.skf-tmp/ as a staging directory (mkdir -p).
             Caller writes files into it, then calls commit-dir to atomically
             swap it into place as <target>/ (with prior target moved aside
             to <target>.skf-rollback-<pid> and removed on success).

  commit-dir Atomically swap <target>.skf-tmp/ into <target>/. If <target>/
             exists, move it to <target>.skf-rollback-<pid> first; on failure,
             restore. Supports rollback via --rollback to undo the most recent
             commit by restoring the rollback dir if still present.

  flip-link  Atomically update symlink <link> to point at <target> using
             the `ln -sfn tmp && mv -Tf tmp link` pattern (or equivalent via
             os.replace on the link path). Holds an flock on <link>.lock.

Cross-platform: locking branches between fcntl (POSIX) and msvcrt
(Windows). Symlink semantics on Windows require dev mode or admin —
flip-link surfaces a clear error rather than silently falling back.
Native Windows is untested in CI; the supported path is WSL2.

Exit codes:
  0 on success
  1 on user error (bad args, missing input)
  2 on operation failure (disk full, permission, race-detected)

CLI examples:
  cat metadata.json | python3 skf-atomic-write.py write --target /path/to/metadata.json
  python3 skf-atomic-write.py stage-dir --target /path/to/1.0.0
  python3 skf-atomic-write.py commit-dir --target /path/to/1.0.0
  python3 skf-atomic-write.py flip-link --link /path/to/active --target 1.0.0
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import sys
from pathlib import Path

if os.name == "nt":
    import msvcrt
else:
    import fcntl


def _acquire_lock(fd: int) -> None:
    """Acquire an exclusive non-blocking lock on fd (auto-released on close/exit)."""
    if os.name == "nt":
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EACCES, errno.EDEADLK):
                raise OSError(errno.EAGAIN, "lock held") from e
            raise
    else:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            if e.errno in (errno.EAGAIN, errno.EACCES):
                raise OSError(errno.EAGAIN, "lock held") from e
            raise


def _release_lock(fd: int) -> None:
    if os.name == "nt":
        try:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
    else:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except OSError:
            pass


def _die(code: int, message: str) -> None:
    print(json.dumps({"status": "error", "message": message}), file=sys.stderr)
    sys.exit(code)


def _ok(payload: dict) -> None:
    payload.setdefault("status", "ok")
    print(json.dumps(payload))


def cmd_write(target: Path) -> None:
    """Write stdin to target atomically via temp + rename."""
    data = sys.stdin.buffer.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".skf-tmp")
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(tmp, target)
    except OSError as e:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        _die(2, f"atomic write failed: {e}")
    _ok({"wrote": str(target), "bytes": len(data)})


def cmd_stage_dir(target: Path) -> None:
    """Create <target>.skf-tmp/ staging directory (clean if present)."""
    staging = target.with_name(target.name + ".skf-tmp")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    _ok({"staging": str(staging)})


def cmd_commit_dir(target: Path, rollback: bool = False) -> None:
    """Swap <target>.skf-tmp/ into <target>/ atomically."""
    staging = target.with_name(target.name + ".skf-tmp")
    rollback_dir = target.with_name(target.name + f".skf-rollback-{os.getpid()}")

    if rollback:
        # Restore from rollback dir (most recent by pid is ambiguous — require explicit one)
        candidates = sorted(target.parent.glob(target.name + ".skf-rollback-*"))
        if not candidates:
            _die(1, f"no rollback dir for {target}")
        chosen = candidates[-1]
        if target.exists():
            shutil.rmtree(target)
        os.replace(chosen, target)
        _ok({"restored": str(target), "from": str(chosen)})
        return

    if not staging.is_dir():
        _die(1, f"staging dir missing: {staging}")

    prior_moved = False
    if target.exists():
        if target.is_symlink() or target.is_file():
            _die(2, f"target is not a directory: {target}")
        try:
            os.replace(target, rollback_dir)
            prior_moved = True
        except OSError as e:
            _die(2, f"failed to move prior target aside: {e}")

    try:
        os.replace(staging, target)
    except OSError as e:
        if prior_moved:
            try:
                os.replace(rollback_dir, target)
            except OSError:
                pass
        _die(2, f"commit swap failed: {e}")

    if prior_moved:
        try:
            shutil.rmtree(rollback_dir)
        except OSError:
            pass

    _ok({"committed": str(target)})


def cmd_flip_link(link: Path, target: str) -> None:
    """Atomically point <link> at <target> using rename-over-symlink pattern.

    target is the value of the symlink (may be relative, as is convention
    for `active -> 1.0.0`). Held lock on <link>.lock prevents concurrent flips.

    On Windows, os.symlink requires Developer Mode or admin. If the symlink
    creation fails with permission/privilege errors, surface a clear error
    rather than fall back silently — callers expect symlink semantics.
    """
    lock_path = link.with_name(link.name + ".skf-lock")
    link.parent.mkdir(parents=True, exist_ok=True)

    # Refuse if existing <link> is not a symlink (avoid rm -rf of real dir)
    if link.exists() and not link.is_symlink():
        _die(2, f"refusing to replace non-symlink: {link}")

    lock_fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        try:
            _acquire_lock(lock_fd)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                _die(2, f"another process holds flip lock on {link}")
            raise

        tmp_link = link.with_name(link.name + ".skf-tmp-link")
        if tmp_link.exists() or tmp_link.is_symlink():
            tmp_link.unlink()
        try:
            os.symlink(target, tmp_link)
        except OSError as e:
            if os.name == "nt" and e.winerror in (1314, 5):  # PRIVILEGE_NOT_HELD or ACCESS_DENIED
                _die(2, "symlink creation requires Windows Developer Mode or admin; use WSL2")
            raise
        os.replace(tmp_link, link)
    finally:
        _release_lock(lock_fd)
        os.close(lock_fd)

    _ok({"link": str(link), "points_to": target})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_write = sub.add_parser("write", help="Atomic file write from stdin")
    p_write.add_argument("--target", type=Path, required=True)

    p_stage = sub.add_parser("stage-dir", help="Create staging directory")
    p_stage.add_argument("--target", type=Path, required=True)

    p_commit = sub.add_parser("commit-dir", help="Commit staging directory to target")
    p_commit.add_argument("--target", type=Path, required=True)
    p_commit.add_argument("--rollback", action="store_true", help="Restore from rollback dir instead of committing")

    p_flip = sub.add_parser("flip-link", help="Atomic symlink flip")
    p_flip.add_argument("--link", type=Path, required=True)
    p_flip.add_argument("--target", type=str, required=True)

    args = parser.parse_args()

    if args.cmd == "write":
        cmd_write(args.target)
    elif args.cmd == "stage-dir":
        cmd_stage_dir(args.target)
    elif args.cmd == "commit-dir":
        cmd_commit_dir(args.target, rollback=args.rollback)
    elif args.cmd == "flip-link":
        cmd_flip_link(args.link, args.target)


if __name__ == "__main__":
    main()
