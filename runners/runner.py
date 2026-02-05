"""
Main benchmark runner that orchestrates all tests.
warmup: is the process of running the benchmark multiple times to warm up the runtime.
trials: is the number of times to run the benchmark.

Example:
python3 run_benchmark.py --runtimes uv --benchmarks pure_python --trials 1 --warmup 0
python3 run_benchmark.py --runtimes uv --benchmarks pure_python --trials 5 --warmup 3
python3 run_benchmark.py --runtimes uv --benchmarks pure_python --trials 10 --warmup 5
python3 run_benchmark.py --runtimes uv --benchmarks pure_python --trials 15 --warmup 7
python3 run_benchmark.py --runtimes uv --benchmarks pure_python --trials 20 --warmup 10
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List
import subprocess

from .runtime_detector import (
    detect_runtimes,
    get_runtime_command,
    print_runtime_summary,
    RuntimeInfo
)
from .timing_utils import (
    measure_startup_time,
    measure_import_time,
    run_multiple_trials,
    measure_memory_usage
)


class BenchmarkRunner:
    """Orchestrates benchmark execution across multiple runtimes."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.benchmarks_dir = os.path.join(project_root, 'benchmarks')
        self.results_dir = os.path.join(project_root, 'results')
        self.runtimes = detect_runtimes()

        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)

    def get_benchmark_files(self) -> Dict[str, str]:
        """Get all benchmark files."""
        benchmarks = {
            'pure_python': os.path.join(self.benchmarks_dir, 'pure_python_math.py'),
            'numpy_scipy': os.path.join(self.benchmarks_dir, 'numpy_scipy_math.py'),
            'mixed_io': os.path.join(self.benchmarks_dir, 'mixed_heavy_io.py'),
        }

        # Verify files exist
        for name, path in list(benchmarks.items()):
            if not os.path.exists(path):
                print(f"WARNING: Benchmark file not found: {path}")
                del benchmarks[name]

        return benchmarks

    def measure_runtime_overhead(self, runtime_name: str, runtime_info: RuntimeInfo) -> Dict:
        """Measure startup time and import overhead for a runtime."""
        print(f"\n  Measuring {runtime_name} overhead...")

        cmd = get_runtime_command(runtime_name, "dummy.py", runtime_info.executable)
        results = {}

        # Measure startup time (multiple runs for accuracy)
        startup_times = []
        for i in range(5):
            startup = measure_startup_time(cmd[:-1] + ['-c', 'pass'])
            if startup > 0:
                startup_times.append(startup)

        if startup_times:
            results['startup_time'] = {
                'average': sum(startup_times) / len(startup_times),
                'min': min(startup_times),
                'max': max(startup_times)
            }
            print(f"    Startup time: {results['startup_time']['average']:.6f}s (avg)")
        else:
            results['startup_time'] = {'average': -1, 'min': -1, 'max': -1}

        # Measure import times for common libraries
        modules = ['sys', 'os', 'time', 'json']
        try:
            import_result = subprocess.run(
                cmd[:-1] + ['-c', 'import numpy'],
                capture_output=True,
                timeout=10
            )
            if import_result.returncode == 0:
                modules.extend(['numpy', 'scipy'])
        except:
            pass

        import_times = measure_import_time(cmd, modules)
        results['import_times'] = import_times

        for module, import_time in import_times.items():
            if import_time > 0:
                print(f"    Import {module}: {import_time:.6f}s")

        return results

    def run_benchmark(
        self,
        runtime_name: str,
        runtime_info: RuntimeInfo,
        benchmark_name: str,
        benchmark_path: str,
        num_trials: int = 3,
        warmup_runs: int = 2
    ) -> Dict:
        """Run a single benchmark on a single runtime."""

        print(f"\n  Running {benchmark_name} on {runtime_name}...")

        # Ensure benchmark_path is absolute for subprocess execution
        benchmark_path = os.path.abspath(benchmark_path)

        cmd = get_runtime_command(runtime_name, benchmark_path, runtime_info.executable)

        # Run the benchmark with multiple trials
        trial_results = run_multiple_trials(
            cmd,
            benchmark_path,
            num_trials=num_trials,
            warmup_runs=warmup_runs
        )

        # Try to measure memory usage (may not work on all platforms)
        # memory_mb = measure_memory_usage(cmd, benchmark_path)
        # trial_results['peak_memory_mb'] = memory_mb

        return trial_results

    def run_all_benchmarks(
        self,
        runtimes_to_test: List[str] = None,
        benchmarks_to_run: List[str] = None,
        num_trials: int = 3,
        warmup_runs: int = 2
    ) -> Dict:
        """Run all benchmarks on all specified runtimes."""

        if runtimes_to_test is None:
            runtimes_to_test = [name for name, info in self.runtimes.items() if info.available]

        if not runtimes_to_test:
            print("ERROR: No available runtimes to test!")
            return {}

        benchmarks = self.get_benchmark_files()

        if benchmarks_to_run:
            benchmarks = {k: v for k, v in benchmarks.items() if k in benchmarks_to_run}

        if not benchmarks:
            print("ERROR: No benchmarks to run!")
            return {}

        print(f"\n{'='*70}")
        print(f"BENCHMARK SUITE")
        print(f"{'='*70}")
        print(f"Runtimes: {', '.join(runtimes_to_test)}")
        print(f"Benchmarks: {', '.join(benchmarks.keys())}")
        print(f"Trials per benchmark: {num_trials}")
        print(f"Warmup runs: {warmup_runs}")
        print(f"{'='*70}")

        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'num_trials': num_trials,
                'warmup_runs': warmup_runs,
                'platform': sys.platform,
            },
            'runtimes': {},
            'benchmarks': {}
        }

        # Measure runtime overhead for each runtime
        print(f"\n{'='*70}")
        print("MEASURING RUNTIME OVERHEAD")
        print(f"{'='*70}")

        for runtime_name in runtimes_to_test:
            runtime_info = self.runtimes.get(runtime_name)
            if not runtime_info or not runtime_info.available:
                print(f"\nSkipping {runtime_name} (not available)")
                continue

            overhead = self.measure_runtime_overhead(runtime_name, runtime_info)
            results['runtimes'][runtime_name] = {
                'name': runtime_info.name,
                'version': runtime_info.version,
                'executable': runtime_info.executable,
                'overhead': overhead
            }

        # Run benchmarks
        print(f"\n{'='*70}")
        print("RUNNING BENCHMARKS")
        print(f"{'='*70}")

        for benchmark_name, benchmark_path in benchmarks.items():
            print(f"\n{'*'*70}")
            print(f"BENCHMARK: {benchmark_name}")
            print(f"{'*'*70}")

            results['benchmarks'][benchmark_name] = {}

            for runtime_name in runtimes_to_test:
                runtime_info = self.runtimes.get(runtime_name)
                if not runtime_info or not runtime_info.available:
                    continue

                try:
                    benchmark_results = self.run_benchmark(
                        runtime_name,
                        runtime_info,
                        benchmark_name,
                        benchmark_path,
                        num_trials=num_trials,
                        warmup_runs=warmup_runs
                    )

                    results['benchmarks'][benchmark_name][runtime_name] = benchmark_results

                    # Print summary
                    if benchmark_results['last_returncode'] == 0:
                        avg = benchmark_results['average']
                        std = benchmark_results['std_dev']
                        print(f"\n    Result: {avg:.4f}s ± {std:.4f}s")
                    else:
                        print(f"\n    Result: FAILED (return code {benchmark_results['last_returncode']})")
                        if benchmark_results['last_stderr']:
                            # #region agent log
                            log_path = "/Users/waqarm/Projects/python-runtime-benchmark/.cursor/debug.log"
                            try:
                                with open(log_path, "a") as f:
                                    import json
                                    f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "C", "location": "runner.py:232", "message": "full stderr captured", "data": {"runtime_name": runtime_name, "benchmark_name": benchmark_name, "returncode": benchmark_results['last_returncode'], "full_stderr": benchmark_results['last_stderr'], "stderr_length": len(benchmark_results['last_stderr'])}, "timestamp": int(time.time() * 1000)}) + "\n")
                            except: pass
                            # #endregion agent log
                            print(f"    Error: {benchmark_results['last_stderr'][:200]}")

                except Exception as e:
                    print(f"\n    ERROR: {e}")
                    results['benchmarks'][benchmark_name][runtime_name] = {
                        'error': str(e),
                        'average': -1
                    }

        return results

    def save_results(self, results: Dict, filename: str = None):
        """Save benchmark results to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"benchmark_results_{timestamp}.json"

        filepath = os.path.join(self.results_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n{'='*70}")
        print(f"Results saved to: {filepath}")
        print(f"{'='*70}")

        return filepath

    def print_summary(self, results: Dict):
        """Print a formatted summary of results."""
        print(f"\n{'='*70}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*70}")

        if 'benchmarks' not in results:
            print("No benchmark results found.")
            return

        for benchmark_name, runtime_results in results['benchmarks'].items():
            print(f"\n{benchmark_name.upper()}:")
            print("-" * 70)

            # Collect valid results
            valid_results = []
            for runtime_name, result in runtime_results.items():
                if isinstance(result, dict) and 'average' in result and result['average'] > 0:
                    valid_results.append((runtime_name, result['average'], result.get('std_dev', 0)))

            if not valid_results:
                print("  No valid results")
                continue

            # Sort by average time
            valid_results.sort(key=lambda x: x[1])

            # Print results
            fastest_time = valid_results[0][1]
            for runtime_name, avg_time, std_dev in valid_results:
                speedup = fastest_time / avg_time
                relative = f"({speedup:.2f}x)" if speedup != 1.0 else "(baseline)"
                print(f"  {runtime_name:12s}: {avg_time:8.4f}s ± {std_dev:6.4f}s  {relative}")

        print(f"\n{'='*70}")


def main():
    """Main entry point for the benchmark runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Python Runtime Benchmark Suite')
    parser.add_argument(
        '--runtimes',
        nargs='+',
        choices=['python3', 'pypy', 'uv'],
        help='Runtimes to test (default: all available)'
    )
    parser.add_argument(
        '--benchmarks',
        nargs='+',
        choices=['pure_python', 'numpy_scipy', 'mixed_io'],
        help='Benchmarks to run (default: all)'
    )
    parser.add_argument(
        '--trials',
        type=int,
        default=3,
        help='Number of trials per benchmark (default: 3)'
    )
    parser.add_argument(
        '--warmup',
        type=int,
        default=2,
        help='Number of warmup runs (default: 2)'
    )
    parser.add_argument(
        '--output',
        help='Output filename for results (default: auto-generated)'
    )

    args = parser.parse_args()

    # Get project root (parent of runners directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    runner = BenchmarkRunner(project_root)

    # Print detected runtimes
    print_runtime_summary(runner.runtimes)

    # Run benchmarks
    results = runner.run_all_benchmarks(
        runtimes_to_test=args.runtimes,
        benchmarks_to_run=args.benchmarks,
        num_trials=args.trials,
        warmup_runs=args.warmup
    )

    # Save and print results
    runner.save_results(results, filename=args.output)
    runner.print_summary(results)


if __name__ == "__main__":
    main()
