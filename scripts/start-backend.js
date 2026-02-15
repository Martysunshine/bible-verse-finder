/**
 * start-backend.js — launches uvicorn using the venv Python.
 */
const { spawn } = require('child_process')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const IS_WIN = process.platform === 'win32'
const PYTHON_BIN = IS_WIN
  ? path.join(ROOT, '.venv', 'Scripts', 'python.exe')
  : path.join(ROOT, '.venv', 'bin', 'python')

const child = spawn(
  PYTHON_BIN,
  ['-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', '8000', '--reload'],
  { cwd: ROOT, stdio: 'inherit' }
)

child.on('exit', (code) => process.exit(code ?? 1))

// Forward kill signals so concurrently can stop it
process.on('SIGINT', () => child.kill('SIGINT'))
process.on('SIGTERM', () => child.kill('SIGTERM'))
