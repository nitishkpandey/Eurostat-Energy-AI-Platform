"""Single-command application launcher.

Starts the ETL pipeline, backend API, and frontend dev server.

Usage:
    uv run python -m backend.dev

The frontend prefers Docker when available, but falls back to a local
npm-based Vite dev server so Windows users do not need to activate a shell
script or run npm from PowerShell directly.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_PORT = 5173
BACKEND_PORT = 8000


def _npm_command(*args: str) -> list[str]:
    """Build a cross-platform npm command for subprocess calls."""
    if os.name == "nt":
        return ["cmd", "/c", "npm", *args]
    return ["npm", *args]


def _run_etl() -> None:
    """Run the ETL pipeline synchronously (fast for SQLite)."""
    print("\n⚡ Running ETL data ingestion…")
    result = subprocess.run(
        [sys.executable, "-m", "backend.etl.main", "--mode", "full-refresh"],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("❌ ETL pipeline failed. Check logs above.", file=sys.stderr)
        sys.exit(result.returncode)
    print("✅ ETL complete — database populated.\n")


def _check_docker() -> bool:
    """Return True if Docker is available and responsive."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_npm() -> bool:
    """Return True if npm is available on the current PATH."""
    try:
        result = subprocess.run(
            _npm_command("--version"),
            capture_output=True,
            timeout=5,
            cwd=ROOT / "frontend",
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _start_local_frontend() -> subprocess.Popen[str] | None:
    """Install frontend deps if needed and launch the Vite dev server."""
    frontend_dir = ROOT / "frontend"
    if not _check_npm():
        return None

    print(f"🌐 Starting frontend on http://localhost:{FRONTEND_PORT} (via local npm)")
    install = subprocess.run(
        _npm_command("install", "--silent"),
        cwd=frontend_dir,
    )
    if install.returncode != 0:
        print("❌ Frontend dependency installation failed.", file=sys.stderr)
        return None

    env = os.environ.copy()
    env["VITE_API_BASE_URL"] = f"http://localhost:{BACKEND_PORT}"
    return subprocess.Popen(
        _npm_command(
            "run",
            "dev",
            "--",
            "--host",
            "0.0.0.0",
            "--port",
            str(FRONTEND_PORT),
        ),
        cwd=frontend_dir,
        env=env,
    )


def main() -> int:
    _run_etl()

    # Start backend
    print(f"🚀 Starting backend on http://localhost:{BACKEND_PORT}")
    backend_env = os.environ.copy()
    backend_env.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    backend_env.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    backend = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.api.main:app",
            "--host", "0.0.0.0",
            "--port", str(BACKEND_PORT),
            "--reload",
        ],
        cwd=ROOT,
        env=backend_env,
    )

    # Start frontend
    frontend = None
    frontend_is_docker = False

    frontend = _start_local_frontend()
    if frontend is None and _check_docker():
        print(f"🌐 Starting frontend on http://localhost:{FRONTEND_PORT} (via Docker)")
        frontend_is_docker = True
        frontend = subprocess.Popen(
            [
                "docker", "run", "--rm",
                "--name", "eurostat_frontend_dev",
                "-p", f"{FRONTEND_PORT}:{FRONTEND_PORT}",
                "-v", f"{ROOT}:/app",
                "-w", "/app/frontend",
                "-e", f"VITE_API_BASE_URL=http://localhost:{BACKEND_PORT}",
                "node:20-alpine",
                "sh", "-c", "npm install --silent && npm run dev -- --host 0.0.0.0 --port 5173",
            ],
            cwd=ROOT,
        )
    elif frontend is None:
        print(
            f"\n⚠️  npm could not be started and Docker is unavailable.\n"
            f"   Install Node.js (https://nodejs.org) and run manually:\n"
            f"   cd frontend && npm install && npm run dev\n"
        )

    print(
        f"\n{'='*60}\n"
        f"  Backend API:  http://localhost:{BACKEND_PORT}/docs\n"
        + (f"  Frontend UI:  http://localhost:{FRONTEND_PORT}\n" if frontend else "")
        + f"  Press Ctrl+C to stop.\n"
        f"{'='*60}\n"
    )

    def shutdown(*_):
        print("\n🛑 Shutting down…")
        backend.terminate()
        if frontend and frontend.poll() is None:
            if frontend_is_docker:
                subprocess.run(["docker", "stop", "eurostat_frontend_dev"], capture_output=True, timeout=10)
            else:
                frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend.poll() is not None:
                print("❌ Backend exited unexpectedly.", file=sys.stderr)
                shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
