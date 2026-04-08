#!/usr/bin/env python3
"""Tests for skf-structural-diff.py."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "skf_diff",
    Path(__file__).parent.parent / "src" / "shared" / "scripts" / "skf-structural-diff.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
diff_exports = mod.diff_exports


@pytest.fixture()
def baseline():
    return [
        {"name": "foo", "file": "src/index.ts", "line": 10, "type": "function"},
        {"name": "Bar", "file": "src/index.ts", "line": 20, "type": "class"},
    ]


class TestNoChanges:
    def test_identical_exports_zero_findings(self, baseline):
        r = diff_exports(baseline, baseline)
        assert r["total_findings"] == 0

    def test_identical_exports_baseline_count(self, baseline):
        r = diff_exports(baseline, baseline)
        assert r["baseline_count"] == 2


class TestAddedExports:
    def test_one_added(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports(baseline, current)
        assert r["by_type"]["added"] == 1

    def test_added_name_is_baz(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports(baseline, current)
        assert r["findings"][0]["name"] == "baz"


class TestRemovedExports:
    def test_one_removed(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports(current, baseline)
        assert r["by_type"]["removed"] == 1

    def test_removed_name_is_baz(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports(current, baseline)
        assert r["findings"][0]["name"] == "baz"


class TestMovedExport:
    def test_one_moved(self, baseline):
        moved_current = [
            {"name": "foo", "file": "src/new-location.ts", "line": 15, "type": "function"},
            {"name": "Bar", "file": "src/index.ts", "line": 20, "type": "class"},
        ]
        r = diff_exports(baseline, moved_current)
        assert r["by_type"]["moved"] == 1

    def test_moved_previous_file(self, baseline):
        moved_current = [
            {"name": "foo", "file": "src/new-location.ts", "line": 15, "type": "function"},
            {"name": "Bar", "file": "src/index.ts", "line": 20, "type": "class"},
        ]
        r = diff_exports(baseline, moved_current)
        moved_finding = [f for f in r["findings"] if f["type"] == "moved"][0]
        assert moved_finding["previous_file"] == "src/index.ts"

    def test_moved_new_file(self, baseline):
        moved_current = [
            {"name": "foo", "file": "src/new-location.ts", "line": 15, "type": "function"},
            {"name": "Bar", "file": "src/index.ts", "line": 20, "type": "class"},
        ]
        r = diff_exports(baseline, moved_current)
        moved_finding = [f for f in r["findings"] if f["type"] == "moved"][0]
        assert moved_finding["file"] == "src/new-location.ts"


class TestChangedSignature:
    def test_one_changed(self):
        base_with_sig = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "function", "signature": "foo(a: string): void"}]
        curr_with_sig = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "function", "signature": "foo(a: string, b: number): void"}]
        r = diff_exports(base_with_sig, curr_with_sig)
        assert r["by_type"]["changed"] == 1

    def test_category_is_signature(self):
        base_with_sig = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "function", "signature": "foo(a: string): void"}]
        curr_with_sig = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "function", "signature": "foo(a: string, b: number): void"}]
        r = diff_exports(base_with_sig, curr_with_sig)
        changed = [f for f in r["findings"] if f["type"] == "changed"][0]
        assert changed["category"] == "signature"


class TestTypeChanged:
    def test_type_change_detected(self):
        base_type = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "function"}]
        curr_type = [{"name": "foo", "file": "src/index.ts", "line": 10, "type": "class"}]
        r = diff_exports(base_type, curr_type)
        assert r["by_type"]["changed"] == 1


class TestEmptyBaseline:
    def test_all_added_from_empty(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports([], current)
        assert r["by_type"]["added"] == 3

    def test_baseline_empty(self, baseline):
        current = baseline + [{"name": "baz", "file": "src/utils.ts", "line": 5, "type": "function"}]
        r = diff_exports([], current)
        assert r["baseline_count"] == 0


class TestEmptyCurrent:
    def test_all_removed(self, baseline):
        r = diff_exports(baseline, [])
        assert r["by_type"]["removed"] == 2


class TestMixedChanges:
    def test_at_least_three_findings(self):
        base = [
            {"name": "a", "file": "src/a.ts", "line": 1, "type": "function"},
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(): void"},
            {"name": "c", "file": "src/c.ts", "line": 1, "type": "const"},
        ]
        curr = [
            {"name": "a", "file": "src/moved.ts", "line": 5, "type": "function"},  # moved
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(x: number): void"},  # signature changed
            {"name": "d", "file": "src/d.ts", "line": 1, "type": "class"},  # added (c removed)
        ]
        r = diff_exports(base, curr)
        assert r["total_findings"] >= 3

    def test_has_moved(self):
        base = [
            {"name": "a", "file": "src/a.ts", "line": 1, "type": "function"},
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(): void"},
            {"name": "c", "file": "src/c.ts", "line": 1, "type": "const"},
        ]
        curr = [
            {"name": "a", "file": "src/moved.ts", "line": 5, "type": "function"},
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(x: number): void"},
            {"name": "d", "file": "src/d.ts", "line": 1, "type": "class"},
        ]
        r = diff_exports(base, curr)
        assert r["by_type"]["moved"] >= 1

    def test_has_changed(self):
        base = [
            {"name": "a", "file": "src/a.ts", "line": 1, "type": "function"},
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(): void"},
            {"name": "c", "file": "src/c.ts", "line": 1, "type": "const"},
        ]
        curr = [
            {"name": "a", "file": "src/moved.ts", "line": 5, "type": "function"},
            {"name": "b", "file": "src/b.ts", "line": 1, "type": "function", "signature": "b(x: number): void"},
            {"name": "d", "file": "src/d.ts", "line": 1, "type": "class"},
        ]
        r = diff_exports(base, curr)
        assert r["by_type"]["changed"] >= 1
