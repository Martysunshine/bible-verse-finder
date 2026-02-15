/**
 * setup.js — ensures Python venv + pip deps + embeddings are ready.
 * Runs automatically before `npm run dev`.
 */
const { execSync, spawnSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const VENV = path.join(ROOT, '.venv')
const IS_WIN = process.platform === 'win32'
const PYTHON_BIN = IS_WIN
  ? path.join(VENV, 'Scripts', 'python.exe')
  : path.join(VENV, 'bin', 'python')
const PIP_BIN = IS_WIN
  ? path.join(VENV, 'Scripts', 'pip.exe')
  : path.join(VENV, 'bin', 'pip')

function run(cmd, opts = {}) {
  console.log(`  > ${cmd}`)
  execSync(cmd, { stdio: 'inherit', cwd: ROOT, ...opts })
}

// 1. Create venv if missing
if (!fs.existsSync(PYTHON_BIN)) {
  console.log('\n🔧 Creating Python virtual environment (.venv)...')
  run('python -m venv .venv')
}

// 2. Install pip dependencies
console.log('\n📦 Installing Python dependencies...')
run(`"${PIP_BIN}" install -r backend/requirements.txt`)

// 3. Build embeddings if missing
const embPath = path.join(ROOT, 'backend', 'data', 'verses.npy')
const metaPath = path.join(ROOT, 'backend', 'data', 'meta.json')
if (!fs.existsSync(embPath) || !fs.existsSync(metaPath)) {
  console.log('\n⚙️  Building embeddings (first run — may take a few minutes)...')
  run(`"${PYTHON_BIN}" backend/prepare_bible.py`)
}

// 4. Install frontend deps
console.log('\n📦 Installing frontend dependencies...')
run('npm install', { cwd: path.join(ROOT, 'frontend') })

console.log('\n✅ Setup complete!\n')
