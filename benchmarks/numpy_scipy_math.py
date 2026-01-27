"""
Heavy math computation using NumPy and SciPy.
Tests performance with optimized C extensions.
branchmark 1: 2000x2000 matrix multiplication
branchmark 2: FFT on 10M data points
branchmark 3: Eigenvalue decomposition (1000x1000)
branchmark 4: SVD decomposition (2000x1000)
branchmark 5: Statistics on 50M elements
branchmark 6: Function optimization (100 iterations)
branchmark 7: Numerical integration (10k iterations)
branchmark 8: Signal filtering (50 iterations)
"""

import sys
import time

try:
    import numpy as np
    from scipy import fft, linalg, optimize, integrate, signal
    SCIPY_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: NumPy/SciPy not available: {e}", flush=True)
    SCIPY_AVAILABLE = False


def run_benchmark():
    """Run all NumPy/SciPy benchmarks."""
    if not SCIPY_AVAILABLE:
        print("Skipping NumPy/SciPy benchmarks - libraries not available", flush=True)
        return {'skipped': 0.0}

    results = {}

    # Benchmark 1: Large matrix operations
    print("  Running: Large matrix multiplication...", flush=True)
    start = time.perf_counter()
    size = 2000
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    c = np.dot(a, b)
    results['matrix_multiply'] = time.perf_counter() - start
    print(f"    Multiplied {size}x{size} matrices in {results['matrix_multiply']:.4f}s")

    # Benchmark 2: FFT operations
    print("  Running: FFT operations...", flush=True)
    start = time.perf_counter()
    signal_data = np.random.rand(10_000_000)
    fft_result = fft.fft(signal_data)
    ifft_result = fft.ifft(fft_result)
    results['fft'] = time.perf_counter() - start
    print(f"    Performed FFT on 10M points in {results['fft']:.4f}s")

    # Benchmark 3: Linear algebra operations
    print("  Running: Eigenvalue decomposition...", flush=True)
    start = time.perf_counter()
    matrix = np.random.rand(1000, 1000)
    eigenvalues, eigenvectors = linalg.eig(matrix)
    results['eigenvalue'] = time.perf_counter() - start
    print(f"    Computed eigenvalues of 1000x1000 matrix in {results['eigenvalue']:.4f}s")

    # Benchmark 4: SVD decomposition
    print("  Running: SVD decomposition...", flush=True)
    start = time.perf_counter()
    matrix = np.random.rand(2000, 1000)
    u, s, vt = linalg.svd(matrix, full_matrices=False)
    results['svd'] = time.perf_counter() - start
    print(f"    Performed SVD on 2000x1000 matrix in {results['svd']:.4f}s")

    # Benchmark 5: Statistical operations
    print("  Running: Statistical computations...", flush=True)
    start = time.perf_counter()
    data = np.random.randn(50_000_000)
    mean = np.mean(data)
    std = np.std(data)
    median = np.median(data)
    percentiles = np.percentile(data, [25, 50, 75, 90, 95, 99])
    results['statistics'] = time.perf_counter() - start
    print(f"    Computed statistics on 50M elements in {results['statistics']:.4f}s")

    # Benchmark 6: Optimization
    print("  Running: Function optimization...", flush=True)
    start = time.perf_counter()

    def rosen(x):
        """Rosenbrock function for optimization."""
        return sum(100.0 * (x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0)

    x0 = np.array([1.3, 0.7, 0.8, 1.9, 1.2])
    for _ in range(100):
        res = optimize.minimize(rosen, x0, method='BFGS')
    results['optimization'] = time.perf_counter() - start
    print(f"    Performed 100 optimizations in {results['optimization']:.4f}s")

    # Benchmark 7: Integration
    print("  Running: Numerical integration...", flush=True)
    start = time.perf_counter()

    def integrand(x, a, b):
        return a * x**2 + b * x

    for i in range(10000):
        result, error = integrate.quad(integrand, 0, 10, args=(2, 3))
    results['integration'] = time.perf_counter() - start
    print(f"    Performed 10k integrations in {results['integration']:.4f}s")

    # Benchmark 8: Signal processing
    print("  Running: Signal filtering...", flush=True)
    start = time.perf_counter()
    t = np.linspace(0, 1, 1_000_000)
    sig = np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 120 * t)
    b, a = signal.butter(4, 100, 'low', fs=1_000_000)
    for _ in range(50):
        filtered = signal.filtfilt(b, a, sig)
    results['signal_filter'] = time.perf_counter() - start
    print(f"    Filtered signal 50 times in {results['signal_filter']:.4f}s")

    return results


if __name__ == "__main__":
    print("NumPy/SciPy Math Benchmark", flush=True)
    print("=" * 50, flush=True)

    results = run_benchmark()

    if 'skipped' not in results:
        print("\nResults:", flush=True)
        total_time = sum(results.values())
        for name, duration in results.items():
            print(f"  {name}: {duration:.4f}s", flush=True)
        print(f"  TOTAL: {total_time:.4f}s", flush=True)
