const { spawn, execSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const projectRoot = path.resolve(__dirname, '..');
const backendDir = path.join(projectRoot, 'backend');
const frontendDir = path.join(projectRoot, 'frontend');

const execFile = (command, args, options = {}) => {
  return execSync(`${command} ${args.join(' ')}`, { shell: true, stdio: 'pipe', ...options });
};

const clearStalePorts = () => {
  const ports = [4000, 5173];

  try {
    const output = execFile('netstat', ['-ano', '-p', 'tcp']);
    const lines = output.toString().split(/\r?\n/);
    const pids = new Set();

    for (const line of lines) {
      const match = line.match(/LISTENING\s+(\d+)$/i) || line.match(/\s+(\d+)\s*$/);
      if (!match) continue;
      const pid = Number(match[1]);
      if (!Number.isInteger(pid) || pid === 0) continue;

      const portLine = line.trim();
      const portMatch = portLine.match(/:(\d+)\s+\S+\s+\S+\s+LISTENING\s+\d+$/i) || portLine.match(/:(\d+)\s+\S+\s+LISTENING\s+\d+$/i);
      if (!portMatch) continue;
      const port = Number(portMatch[1]);
      if (ports.includes(port)) {
        pids.add(pid);
      }
    }

    for (const pid of pids) {
      try {
        execFile('taskkill', ['/PID', String(pid), '/F']);
        console.log(`Cleared stale process on port ${pid}`);
      } catch {
        // ignore failed cleanup attempts
      }
    }
  } catch {
    // ignore when netstat is unavailable
  }
};

const ensureEnvFile = () => {
  const rootEnv = path.join(projectRoot, '.env');
  if (!fs.existsSync(rootEnv)) {
    const example = path.join(projectRoot, '.env.example');
    if (fs.existsSync(example)) {
      fs.copyFileSync(example, rootEnv);
      console.log('Created .env from .env.example');
    }
  }

  const backendEnv = path.join(backendDir, '.env');
  if (!fs.existsSync(backendEnv)) {
    const example = path.join(backendDir, '.env.example');
    if (fs.existsSync(example)) {
      fs.copyFileSync(example, backendEnv);
      console.log('Created backend/.env from backend/.env.example');
    }
  }

  const frontendEnv = path.join(frontendDir, '.env');
  if (!fs.existsSync(frontendEnv)) {
    const example = path.join(frontendDir, '.env.example');
    if (fs.existsSync(example)) {
      fs.copyFileSync(example, frontendEnv);
      console.log('Created frontend/.env from frontend/.env.example');
    }
  }
};

const isContainerRunning = () => {
  try {
    const output = execSync('docker ps --format "{{.Names}}"', { stdio: ['ignore', 'pipe', 'pipe'] }).toString();
    return output.includes('stap-postgres');
  } catch {
    return false;
  }
};

const ensurePostgres = () => {
  try {
    execSync('docker --version', { stdio: 'ignore' });
    const status = execSync('docker compose ps --format "{{.Service}} {{.State}}"', { cwd: projectRoot, stdio: ['ignore', 'pipe', 'pipe'] }).toString();
    const hasPostgres = status.toLowerCase().includes('postgres');

    if (!hasPostgres || !isContainerRunning()) {
      console.log('Starting PostgreSQL container...');
      execSync('docker compose up -d postgres', { cwd: projectRoot, stdio: 'inherit' });
    }
  } catch {
    console.warn('Docker is not available or PostgreSQL is not managed here. If you are using an external database, make sure it is running.');
  }
};

const run = (name, command, cwd) => {
  const child = spawn(command, { cwd, shell: true, stdio: 'inherit' });
  child.on('exit', (code) => {
    if (code !== 0) {
      console.error(`${name} exited with code ${code}`);
      process.exit(code || 1);
    }
  });
  return child;
};

ensureEnvFile();
clearStalePorts();
ensurePostgres();

console.log('Starting backend and frontend...');

run('backend', 'npm run dev', backendDir);
run('frontend', 'npm run dev', frontendDir);

process.on('SIGINT', () => process.exit(0));
process.on('SIGTERM', () => process.exit(0));
