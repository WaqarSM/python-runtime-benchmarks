"""
Detect and validate available Python runtimes.
"""

import subprocess
import shutil
import sys
import os
from typing import Dict, List, Optional


class RuntimeInfo:
    """Information about a Python runtime."""

    def __init__(self, name: str, executable: str, version: str, available: bool, numpy_version: str = None, scipy_version: str = None):
        self.name = name
        self.executable = executable
        self.version = version
        self.available = available
        self.numpy_version = numpy_version
        self.scipy_version = scipy_version

    def __repr__(self):
        status = "available" if self.available else "not available"
        if self.available:
            libs = []
            if self.numpy_version:
                libs.append(f"numpy={self.numpy_version}")
            if self.scipy_version:
                libs.append(f"scipy={self.scipy_version}")
            lib_str = f" [{', '.join(libs)}]" if libs else ""
            return f"{self.name} ({self.version}) - {status}{lib_str}"
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


def get_library_versions(executable: str) -> tuple[Optional[str], Optional[str]]:
    """Check for numpy and scipy versions."""
    numpy_ver = None
    scipy_ver = None
    
    # Check numpy
    try:
        res = subprocess.run(
            [executable, "-c", "import numpy; print(numpy.__version__)"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0:
            numpy_ver = res.stdout.strip()
    except: pass
    
    # Check scipy
    try:
        res = subprocess.run(
            [executable, "-c", "import scipy; print(scipy.__version__)"],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0:
            scipy_ver = res.stdout.strip()
    except: pass
    
    return numpy_ver, scipy_ver


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
    cwd = os.getcwd()

    # Check CPython (prefer .venv)
    venv_python = os.path.join(cwd, ".venv", "bin", "python")
    if os.path.exists(venv_python):
        executable = venv_python
    else:
        executable = shutil.which("python3")

    if executable:
        version = get_runtime_version(executable)
        np_ver, sp_ver = get_library_versions(executable) if version else (None, None)
        runtimes['python3'] = RuntimeInfo(
            name='CPython',
            executable=executable,
            version=version or "unknown",
            available=version is not None,
            numpy_version=np_ver,
            scipy_version=sp_ver
        )
    else:
        runtimes['python3'] = RuntimeInfo(
            name='CPython', executable='python3', version='', available=False
        )

    # Check PyPy (prefer .venv-pypy)
    venv_pypy = os.path.join(cwd, ".venv-pypy", "bin", "pypy3")
    # Fallback to bin/python if pypy3 doesn't exist in venv (sometimes it's just python)
    if not os.path.exists(venv_pypy):
         venv_pypy_alt = os.path.join(cwd, ".venv-pypy", "bin", "python")
         if os.path.exists(venv_pypy_alt):
             venv_pypy = venv_pypy_alt

    if os.path.exists(venv_pypy):
        executable = venv_pypy
    else:
        executable = shutil.which("pypy3")

    if executable:
        version = get_runtime_version(executable)
        np_ver, sp_ver = get_library_versions(executable) if version else (None, None)
        runtimes['pypy'] = RuntimeInfo(
            name='PyPy',
            executable=executable,
            version=version or "unknown",
            available=version is not None,
            numpy_version=np_ver,
            scipy_version=sp_ver
        )
    else:
        runtimes['pypy'] = RuntimeInfo(
            name='PyPy', executable='pypy3', version='', available=False
        )

    # Check uv
    uv_path, uv_version = check_uv_runtime()
    if uv_path and uv_version:
        # UV just runs python, so checking its libs is tricky without a specific project context context, 
        # but the request was specifically for the runtimes.
        runtimes['uv'] = RuntimeInfo(
            name='UV',
            executable=uv_path,
            version=uv_version,
            available=True
        )
    else:
        runtimes['uv'] = RuntimeInfo(
            name='UV', executable='uv', version='', available=False
        )

    return runtimes


def get_runtime_command(runtime_name: str, script_path: str, executable: str = None) -> List[str]:
    """Get the command to execute a script with the given runtime."""
    # #region agent log
    log_path = "/Users/waqarm/Projects/python-runtime-benchmark/.cursor/debug.log"
    try:
        import json, os, time
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "post-fix", "hypothesisId": "A", "location": "runtime_detector.py:137", "message": "get_runtime_command called", "data": {"runtime_name": runtime_name, "script_path": script_path, "executable": executable, "cwd": os.getcwd()}, "timestamp": int(time.time() * 1000)}) + "\n")
    except: pass
    # #endregion agent log
    
    if runtime_name == 'uv':
        # Use --no-project to skip building the project as a package
        cmd = ['uv', 'run', '--no-project', 'python', script_path]
        return cmd
    
    # For others, use the provided executable (from venv) or fall back to defaults
    exe = executable or ('pypy3' if runtime_name == 'pypy' else 'python3')
    return [exe, script_path]


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
