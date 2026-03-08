const { program } = require('commander');
const installCommand = require('./commands/install');
const statusCommand = require('./commands/status');

// Fix for stdin issues when running through npm on Windows
if (process.stdin.isTTY) {
  try {
    process.stdin.resume();
    process.stdin.setEncoding('utf8');
    if (process.platform === 'win32') {
      process.stdin.on('error', () => {});
    }
  } catch {
    // Silently ignore - some environments may not support these operations
  }
}

const packageJson = require('../../package.json');

program.version(packageJson.version).description('Skill Forge — Evidence-Based Agent Skills Compiler');

for (const command of [installCommand, statusCommand]) {
  const cmd = program.command(command.command).description(command.description);
  for (const option of command.options || []) {
    cmd.option(...option);
  }
  cmd.action(command.action);
}

program.parse(process.argv);

if (process.argv.slice(2).length === 0) {
  program.outputHelp();
}
