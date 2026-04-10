from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import TextIO


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_line(log_file: TextIO, message: str) -> None:
    line = f"[{timestamp()}] {message}"
    print(line, flush=True)
    log_file.write(f"{line}\n")
    log_file.flush()


def stream_process_output(name: str, process: subprocess.Popen[str], log_file: TextIO) -> None:
    assert process.stdout is not None
    for raw_line in process.stdout:
        clean = raw_line.rstrip("\n")
        if not clean:
            continue
        stamped = f"[{timestamp()}] [{name}] {clean}"
        print(stamped, flush=True)
        log_file.write(f"{stamped}\n")
        log_file.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run backend + frontend with persistent logs."
    )
    parser.add_argument("--backend-host", default="0.0.0.0")
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--frontend-host", default="0.0.0.0")
    parser.add_argument("--frontend-port", type=int, default=5173)
    parser.add_argument("--frontend-api-base-url", default="http://localhost:8000")
    parser.add_argument(
        "--install-frontend",
        action="store_true",
        help="Run npm install before starting Vite.",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable backend auto-reload.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    root_dir = Path(__file__).resolve().parents[1]
    frontend_dir = root_dir / "frontend"
    log_dir = root_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    main_log_path = log_dir / "main.log"
    backend_log_path = log_dir / "backend.log"
    frontend_log_path = log_dir / "frontend.log"

    if shutil.which("npm") is None:
        print("npm is not available on PATH. Please install Node.js/npm first.", file=sys.stderr)
        return 1

    with (
        main_log_path.open("a", encoding="utf-8") as main_log,
        backend_log_path.open("a", encoding="utf-8") as backend_log,
        frontend_log_path.open("a", encoding="utf-8") as frontend_log,
    ):
        separator = "=" * 72
        for target in (main_log, backend_log, frontend_log):
            target.write(f"\n{separator}\n[{timestamp()}] New run\n")
            target.flush()

        write_line(main_log, f"Project root: {root_dir}")
        write_line(main_log, f"Log directory: {log_dir}")

        if args.install_frontend:
            write_line(main_log, "Running npm install for frontend dependencies.")
            install_cmd = ["npm", "install"]
            install_result = subprocess.run(
                install_cmd,
                cwd=frontend_dir,
                stdout=frontend_log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            write_line(main_log, f"npm install finished with code {install_result.returncode}.")
            if install_result.returncode != 0:
                write_line(main_log, "Stopping because frontend dependency install failed.")
                return install_result.returncode

        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.api.main:app",
            "--host",
            args.backend_host,
            "--port",
            str(args.backend_port),
        ]
        if not args.no_reload:
            backend_cmd.append("--reload")

        frontend_cmd = [
            "npm",
            "run",
            "dev",
            "--",
            "--host",
            args.frontend_host,
            "--port",
            str(args.frontend_port),
            "--strictPort",
        ]

        frontend_env = os.environ.copy()
        frontend_env["VITE_API_BASE_URL"] = args.frontend_api_base_url

        write_line(main_log, f"Starting backend: {' '.join(backend_cmd)}")
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        write_line(main_log, f"Starting frontend: {' '.join(frontend_cmd)}")
        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            env=frontend_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        backend_thread = threading.Thread(
            target=stream_process_output,
            args=("backend", backend_proc, backend_log),
            daemon=True,
        )
        frontend_thread = threading.Thread(
            target=stream_process_output,
            args=("frontend", frontend_proc, frontend_log),
            daemon=True,
        )
        backend_thread.start()
        frontend_thread.start()

        processes = {
            "backend": backend_proc,
            "frontend": frontend_proc,
        }

        shutdown_requested = False
        final_code = 0

        def request_shutdown(reason: str) -> None:
            nonlocal shutdown_requested, final_code
            if shutdown_requested:
                return

            shutdown_requested = True
            write_line(main_log, f"Shutdown requested: {reason}")

            for name, proc in processes.items():
                if proc.poll() is None:
                    write_line(main_log, f"Sending SIGTERM to {name} (pid={proc.pid}).")
                    proc.terminate()

            deadline = time.time() + 8
            while time.time() < deadline:
                alive = [proc for proc in processes.values() if proc.poll() is None]
                if not alive:
                    break
                time.sleep(0.2)

            for name, proc in processes.items():
                if proc.poll() is None:
                    write_line(main_log, f"Force killing {name} (pid={proc.pid}).")
                    proc.kill()

            for name, proc in processes.items():
                code = proc.wait(timeout=5)
                write_line(main_log, f"{name} exited with code {code}.")
                if final_code == 0 and code != 0:
                    final_code = code

        def handle_signal(signum: int, _frame: object) -> None:
            signal_name = signal.Signals(signum).name
            request_shutdown(f"received {signal_name}")

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        write_line(
            main_log,
            (
                "Application started. Frontend: "
                f"http://localhost:{args.frontend_port} | Backend: http://localhost:{args.backend_port}"
            ),
        )

        try:
            while not shutdown_requested:
                for name, proc in processes.items():
                    code = proc.poll()
                    if code is not None:
                        if code != 0:
                            final_code = code
                        request_shutdown(f"{name} exited unexpectedly with code {code}")
                        break
                time.sleep(0.3)
        except KeyboardInterrupt:
            request_shutdown("keyboard interrupt")

        write_line(main_log, f"run-app finished with code {final_code}.")
        return final_code


if __name__ == "__main__":
    raise SystemExit(main())
