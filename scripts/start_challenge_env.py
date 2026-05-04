#!/usr/bin/env python3
"""Start the local services needed for IoT Challenge 3.

This script starts:
- Mosquitto on localhost:1884
- Node-RED on localhost:1880

Press Ctrl+C to stop the processes started by this script.
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
DEFAULT_FLOW = ROOT / "code" / "flows.json"
MOSQUITTO_X86 = Path(r"C:\Program Files (x86)\Mosquitto\mosquitto.exe")
MOSQUITTO_X64 = Path(r"C:\Program Files\mosquitto\mosquitto.exe")


def port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_executable(name: str, fallbacks: list[Path] | None = None) -> str:
    found = shutil.which(name)
    if found:
        return found

    for fallback in fallbacks or []:
        if fallback.exists():
            return str(fallback)

    raise FileNotFoundError(
        f"Cannot find {name}. Add it to PATH or install it first."
    )


def stream_output(prefix: str, proc: subprocess.Popen[str], log_file: Path) -> None:
    with log_file.open("a", encoding="utf-8", errors="replace") as log:
        assert proc.stdout is not None
        for line in proc.stdout:
            text = line.rstrip()
            log.write(line)
            log.flush()
            if text:
                print(f"[{prefix}] {text}")


def start_process(
    name: str,
    command: list[str],
    log_file: Path,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> subprocess.Popen[str]:
    print(f"Starting {name}: {' '.join(command)}")
    proc = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    thread = threading.Thread(
        target=stream_output,
        args=(name, proc, log_file),
        daemon=True,
    )
    thread.start()
    return proc


def wait_for_port(name: str, host: str, port: int, seconds: int = 20) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if port_open(host, port):
            print(f"{name} is listening on {host}:{port}")
            return True
        time.sleep(0.5)
    print(f"Warning: {name} did not open {host}:{port} within {seconds}s")
    return False


def terminate_processes(processes: list[tuple[str, subprocess.Popen[str]]]) -> None:
    for name, proc in processes:
        if proc.poll() is None:
            print(f"Stopping {name}...")
            proc.terminate()

    deadline = time.time() + 8
    for name, proc in processes:
        while proc.poll() is None and time.time() < deadline:
            time.sleep(0.2)
        if proc.poll() is None:
            print(f"Force stopping {name}...")
            proc.kill()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start Mosquitto and Node-RED for IoT Challenge 3."
    )
    parser.add_argument("--mosquitto-port", type=int, default=1884)
    parser.add_argument("--node-red-port", type=int, default=1880)
    parser.add_argument("--no-mosquitto", action="store_true")
    parser.add_argument("--no-node-red", action="store_true")
    parser.add_argument(
        "--flow",
        type=Path,
        default=None,
        help=(
            "Optional Node-RED flow file to pass to node-red. "
            "If omitted, Node-RED uses its default user directory."
        ),
    )
    return parser.parse_args()


def load_dotenv(path: Path) -> dict[str, str]:
    env = os.environ.copy()
    if not path.exists():
        return env

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in env:
            env[key] = value

    return env


def main() -> int:
    args = parse_args()
    LOG_DIR.mkdir(exist_ok=True)
    process_env = load_dotenv(ROOT / ".env")
    processes: list[tuple[str, subprocess.Popen[str]]] = []

    try:
        if not args.no_mosquitto:
            if port_open("localhost", args.mosquitto_port):
                print(f"Mosquitto seems already running on localhost:{args.mosquitto_port}")
            else:
                mosquitto = find_executable(
                    "mosquitto",
                    [MOSQUITTO_X86, MOSQUITTO_X64],
                )
                proc = start_process(
                    "mosquitto",
                    [mosquitto, "-p", str(args.mosquitto_port), "-v"],
                    LOG_DIR / "mosquitto.log",
                    env=process_env,
                )
                processes.append(("mosquitto", proc))
                wait_for_port("Mosquitto", "localhost", args.mosquitto_port)

        if not args.no_node_red:
            if port_open("localhost", args.node_red_port):
                print(f"Node-RED seems already running on localhost:{args.node_red_port}")
            else:
                node_red = find_executable("node-red")
                command = [node_red, "-p", str(args.node_red_port)]

                if args.flow is not None:
                    flow_path = args.flow
                    if not flow_path.is_absolute():
                        flow_path = ROOT / flow_path
                    if not flow_path.exists():
                        raise FileNotFoundError(f"Flow file not found: {flow_path}")
                    command.append(str(flow_path))

                proc = start_process(
                    "node-red",
                    command,
                    LOG_DIR / "node-red.log",
                    env=process_env,
                )
                processes.append(("node-red", proc))
                wait_for_port("Node-RED", "localhost", args.node_red_port, seconds=35)

        print()
        print("Environment ready.")
        print(f"- Mosquitto: localhost:{args.mosquitto_port}")
        print(f"- Node-RED:  http://localhost:{args.node_red_port}")
        print(f"- Logs:      {LOG_DIR}")
        print()
        print("Useful MQTT test:")
        print(
            f"  mosquitto_sub -h localhost -p {args.mosquitto_port} "
            "-t challenge3/id_generator -v"
        )
        print()
        print("Press Ctrl+C here to stop services started by this script.")

        if not processes:
            print("No new processes were started because the required ports are already in use.")
            return 0

        while True:
            for name, proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"{name} exited with code {code}")
                    return code
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        terminate_processes(processes)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        terminate_processes(processes)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
