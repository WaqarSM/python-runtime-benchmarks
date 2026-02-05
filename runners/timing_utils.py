"""
Timing utilities for precise benchmarking.
"""

import subprocess
import time
import tempfile
import os
from typing import Dict, Tuple, List
import json


def measure_startup_time(runtime_command: List[str]) -> float:
    """
    Measure cold start time of a runtime.
    Time from process creation to Python being ready.
    """
    # Create a minimal script that just exits
    startup_script = "import sys; sys.exit(0)"

    start = time.perf_counter()
    try:
        result = subprocess.run(
            runtime_command[:-1] + ['-c', startup_script],
            capture_output=True,
            timeout=30
        )
        duration = time.perf_counter() - start
        return duration if result.returncode == 0 else -1
    except subprocess.TimeoutExpired:
        return -1


def measure_import_time(runtime_command: List[str], modules: List[str]) -> Dict[str, float]:
    """
    Measure time to import specific modules.
    """
    results = {}

    for module in modules:
        import_script = f"import time; start=time.perf_counter(); import {module}; print(time.perf_counter()-start)"

        try:
            result = subprocess.run(
                runtime_command[:-1] + ['-c', import_script],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                try:
                    import_time = float(result.stdout.strip())
                    results[module] = import_time
                except ValueError:
                    results[module] = -1
            else:
                results[module] = -1
        except subprocess.TimeoutExpired:
            results[module] = -1

    return results


def run_benchmark_subprocess(
    runtime_command: List[str],
    script_path: str,
    warmup_runs: int = 0
) -> Tuple[float, str, str, int]:
    """
    Run a benchmark script in a subprocess and measure execution time.

    Returns:
        (execution_time, stdout, stderr, return_code)
    """
    # #region agent log
    log_path = "/Users/waqarm/Projects/python-runtime-benchmark/.cursor/debug.log"
    try:
        with open(log_path, "a") as f:
            import json
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "timing_utils.py:77", "message": "run_benchmark_subprocess entry", "data": {"runtime_command": runtime_command, "script_path": script_path, "warmup_runs": warmup_runs}, "timestamp": int(time.time() * 1000)}) + "\n")
    except: pass
    # #endregion agent log
    
    # Warmup runs (important for PyPy JIT)
    for _ in range(warmup_runs):
        try:
            subprocess.run(
                runtime_command + [script_path],
                capture_output=True,
                timeout=600  # 10 minute timeout for warmup
            )
        except subprocess.TimeoutExpired:
            pass

    # Actual timed run
    start = time.perf_counter()
    try:
        result = subprocess.run(
            runtime_command + [script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        duration = time.perf_counter() - start

        # #region agent log
        try:
            with open(log_path, "a") as f:
                import json
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "C", "location": "timing_utils.py:98", "message": "subprocess result", "data": {"returncode": result.returncode, "stdout_length": len(result.stdout), "stderr_length": len(result.stderr), "stderr_preview": result.stderr[:500] if result.stderr else "", "full_stderr": result.stderr if result.stderr else ""}, "timestamp": int(time.time() * 1000)}) + "\n")
        except: pass
        # #endregion agent log

        return duration, result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        duration = time.perf_counter() - start
        return duration, "", "TIMEOUT", -1


def run_multiple_trials(
    runtime_command: List[str],
    script_path: str,
    num_trials: int = 3,
    warmup_runs: int = 2
) -> Dict:
    """
    Run multiple trials of a benchmark and collect statistics.

    Returns:
        Dictionary with timing statistics and output from the last run.
    """
    print(f"    Running {warmup_runs} warmup iterations...", flush=True)

    # Do warmup runs once
    for i in range(warmup_runs):
        try:
            subprocess.run(
                runtime_command + [script_path],
                capture_output=True,
                timeout=600
            )
            print(f"      Warmup {i+1}/{warmup_runs} complete", flush=True)
        except subprocess.TimeoutExpired:
            print(f"      Warmup {i+1}/{warmup_runs} timed out", flush=True)

    print(f"    Running {num_trials} timed trials...", flush=True)

    # Timed runs
    times = []
    last_stdout = ""
    last_stderr = ""
    last_returncode = 0

    for trial in range(num_trials):
        duration, stdout, stderr, returncode = run_benchmark_subprocess(
            runtime_command, script_path, warmup_runs=0
        )

        times.append(duration)
        last_stdout = stdout
        last_stderr = stderr
        last_returncode = returncode

        print(f"      Trial {trial+1}/{num_trials}: {duration:.4f}s", flush=True)

        if returncode != 0:
            print(f"      WARNING: Trial {trial+1} failed with code {returncode}", flush=True)

    # Calculate statistics
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # Calculate standard deviation
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5

        return {
            'times': times,
            'average': avg_time,
            'min': min_time,
            'max': max_time,
            'std_dev': std_dev,
            'num_trials': num_trials,
            'warmup_runs': warmup_runs,
            'last_stdout': last_stdout,
            'last_stderr': last_stderr,
            'last_returncode': last_returncode
        }
    else:
        return {
            'times': [],
            'average': -1,
            'min': -1,
            'max': -1,
            'std_dev': -1,
            'num_trials': 0,
            'warmup_runs': warmup_runs,
            'last_stdout': last_stdout,
            'last_stderr': last_stderr,
            'last_returncode': last_returncode
        }


def measure_memory_usage(runtime_command: List[str], script_path: str) -> int:
    """
    Attempt to measure peak memory usage (in MB).
    Note: This is platform-dependent and may not work everywhere.
    """
    try:
        # Try using /usr/bin/time on Unix-like systems
        time_cmd = ['/usr/bin/time', '-l'] + runtime_command + [script_path]

        result = subprocess.run(
            time_cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        # Parse output for maximum resident set size
        for line in result.stderr.split('\n'):
            if 'maximum resident set size' in line:
                # Extract number (in bytes on macOS, KB on Linux)
                parts = line.split()
                if len(parts) >= 1:
                    try:
                        size_bytes = int(parts[0])
                        # Convert to MB (assuming bytes)
                        return size_bytes // (1024 * 1024)
                    except ValueError:
                        pass

        return -1

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1


if __name__ == "__main__":
    # Test timing utilities
    # When run directly, add project root to path for imports
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    print("Testing timing utilities...")
    print()

    from runners.runtime_detector import detect_runtimes, get_runtime_command

    runtimes = detect_runtimes()

    for name, info in runtimes.items():
        if info.available:
            print(f"Testing {name}:")

            # Test startup time
            cmd = get_runtime_command(name, "dummy.py", info.executable)
            startup = measure_startup_time(cmd[:-1] + ['-c', 'pass'])
            print(f"  Startup time: {startup:.6f}s")

            # Test import times
            imports = measure_import_time(cmd, ['sys', 'os'])
            for module, import_time in imports.items():
                print(f"  Import {module}: {import_time:.6f}s")

            print()
