"""
Detect and validate available Python runtimes.
"""

import subprocess
import shutil
import sys
from typing import Dict, List, Optional


class RuntimeInfo:
    """Information about a Python runtime."""

    def __init__(self, name: str, executable: str, version: str, available: bool):
        self.name = name
        self.executable = executable
        self.version = version
        self.available = available

    def __repr__(self):
        status = "available" if self.available else "not available"
        if self.available:
            return f"{self.name} ({self.version}) - {status}"
        return f"{self.name} - {status}"


def get_runtime_version(executable: str) -> Optional[str]:
    """Get version string for a Python runtime."""
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Python version can be in stdout or stderr
        version_output = result.stdout or result.stderr
        return version_output.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return None


def check_uv_runtime() -> tuple[Optional[str], Optional[str]]:
    """Check if uv is available and how it runs Python."""
    uv_path = shutil.which("uv")
    if not uv_path:
        return None, None

    try:
        # Check uv version
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        uv_version = result.stdout.strip()

        # Check if uv can run Python
        result = subprocess.run(
            ["uv", "run", "python", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            python_version = (result.stdout or result.stderr).strip()
            return uv_path, f"{uv_version} (Python: {python_version})"

        return uv_path, uv_version
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return uv_path, "unknown version"


def detect_runtimes() -> Dict[str, RuntimeInfo]:
    """Detect all available Python runtimes."""
    runtimes = {}

    # Check CPython (standard python3)
    python3_path = shutil.which("python3")
    if python3_path:
        version = get_runtime_version(python3_path)
        runtimes['python3'] = RuntimeInfo(
            name='CPython',
            executable=python3_path,
            version=version or "unknown",
            available=version is not None
        )
    else:
        runtimes['python3'] = RuntimeInfo(
            name='CPython',
            executable='python3',
            version='',
            available=False
        )

    # Check PyPy
    pypy3_path = shutil.which("pypy3")
    if pypy3_path:
        version = get_runtime_version(pypy3_path)
        runtimes['pypy'] = RuntimeInfo(
            name='PyPy',
            executable=pypy3_path,
            version=version or "unknown",
            available=version is not None
        )
    else:
        runtimes['pypy'] = RuntimeInfo(
            name='PyPy',
            executable='pypy3',
            version='',
            available=False
        )

    # Check uv
    uv_path, uv_version = check_uv_runtime()
    if uv_path and uv_version:
        runtimes['uv'] = RuntimeInfo(
            name='UV',
            executable=uv_path,
            version=uv_version,
            available=True
        )
    else:
        runtimes['uv'] = RuntimeInfo(
            name='UV',
            executable='uv',
            version='',
            available=False
        )

    return runtimes


def get_runtime_command(runtime_name: str, script_path: str) -> List[str]:
    """Get the command to execute a script with the given runtime."""
    # #region agent log
    log_path = "/Users/waqarm/Projects/python-runtime-benchmark/.cursor/debug.log"
    try:
        import json, os, time
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "post-fix", "hypothesisId": "A", "location": "runtime_detector.py:137", "message": "get_runtime_command called", "data": {"runtime_name": runtime_name, "script_path": script_path, "cwd": os.getcwd()}, "timestamp": int(time.time() * 1000)}) + "\n")
    except: pass
    # #endregion agent log
    
    if runtime_name == 'uv':
        # Use --no-project to skip building the project as a package
        cmd = ['uv', 'run', '--no-project', 'python', script_path]
        # #region agent log
        try:
            import json, time
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "post-fix", "hypothesisId": "A", "location": "runtime_detector.py:143", "message": "uv command constructed with --no-project", "data": {"command": cmd}, "timestamp": int(time.time() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        return cmd
    elif runtime_name == 'pypy':
        return ['pypy3', script_path]
    else:  # python3
        return ['python3', script_path]


def print_runtime_summary(runtimes: Dict[str, RuntimeInfo]):
    """Print a summary of detected runtimes."""
    print("\nDetected Python Runtimes:")
    print("=" * 60)
    for name, info in runtimes.items():
        status = "✓" if info.available else "✗"
        print(f"  {status} {info}")
    print()


if __name__ == "__main__":
    runtimes = detect_runtimes()
    print_runtime_summary(runtimes)

    available_count = sum(1 for r in runtimes.values() if r.available)
    print(f"Total available runtimes: {available_count}/{len(runtimes)}")
