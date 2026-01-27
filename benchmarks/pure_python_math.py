"""
Heavy math computation using pure Python.
No external dependencies - tests raw Python performance.
branchmark 1: Prime number generation (up to 50,000)
branchmark 2: Recursive Fibonacci (up to n=30)
branchmark 3: Iterative Fibonacci (up to n=10,000)
branchmark 4: 100x100 matrix multiplication in pure Python
branchmark 5: 800x600 Mandelbrot set calculation
"""

import sys
import time


def is_prime(n):
    """Check if a number is prime using trial division."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def find_primes(limit):
    """Find all prime numbers up to limit."""
    primes = []
    for num in range(2, limit):
        if is_prime(num):
            primes.append(num)
    return primes


def fibonacci_recursive(n):
    """Calculate Fibonacci number recursively (inefficient on purpose)."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_iterative(n):
    """Calculate Fibonacci number iteratively."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def matrix_multiply_python(a, b):
    """Multiply two matrices using pure Python (no numpy)."""
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])

    if cols_a != rows_b:
        raise ValueError("Matrix dimensions don't match")

    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]

    return result


def generate_matrix(size):
    """Generate a square matrix filled with values."""
    return [[i * size + j for j in range(size)] for i in range(size)]


def calculate_mandelbrot(width, height, max_iter=100):
    """Calculate Mandelbrot set for given dimensions."""
    result = []
    for y in range(height):
        row = []
        for x in range(width):
            # Map pixel to complex plane
            c = complex(-2.5 + (x / width) * 3.5, -1.25 + (y / height) * 2.5)
            z = 0
            iterations = 0

            while abs(z) <= 2 and iterations < max_iter:
                z = z * z + c
                iterations += 1

            row.append(iterations)
        result.append(row)

    return result


def run_benchmark():
    """Run all pure Python benchmarks."""
    results = {}

    # Benchmark 1: Prime number generation
    print("  Running: Prime number generation...", flush=True)
    start = time.perf_counter()
    primes = find_primes(50000)
    results['primes'] = time.perf_counter() - start
    print(f"    Found {len(primes)} primes in {results['primes']:.4f}s")

    # Benchmark 2: Recursive Fibonacci (smaller numbers to avoid timeout)
    print("  Running: Recursive Fibonacci...", flush=True)
    start = time.perf_counter()
    fib_results = [fibonacci_recursive(i) for i in range(30)]
    results['fibonacci_recursive'] = time.perf_counter() - start
    print(f"    Calculated {len(fib_results)} Fibonacci numbers in {results['fibonacci_recursive']:.4f}s")

    # Benchmark 3: Iterative Fibonacci (larger numbers)
    print("  Running: Iterative Fibonacci...", flush=True)
    start = time.perf_counter()
    fib_large = [fibonacci_iterative(i) for i in range(10000)]
    results['fibonacci_iterative'] = time.perf_counter() - start
    print(f"    Calculated {len(fib_large)} Fibonacci numbers in {results['fibonacci_iterative']:.4f}s")

    # Benchmark 4: Matrix multiplication
    print("  Running: Matrix multiplication...", flush=True)
    start = time.perf_counter()
    matrix_a = generate_matrix(100)
    matrix_b = generate_matrix(100)
    result_matrix = matrix_multiply_python(matrix_a, matrix_b)
    results['matrix_multiply'] = time.perf_counter() - start
    print(f"    Multiplied 100x100 matrices in {results['matrix_multiply']:.4f}s")

    # Benchmark 5: Mandelbrot set calculation
    print("  Running: Mandelbrot set calculation...", flush=True)
    start = time.perf_counter()
    mandelbrot = calculate_mandelbrot(800, 600, max_iter=100)
    results['mandelbrot'] = time.perf_counter() - start
    print(f"    Calculated 800x600 Mandelbrot set in {results['mandelbrot']:.4f}s")

    return results


if __name__ == "__main__":
    print("Pure Python Math Benchmark", flush=True)
    print("=" * 50, flush=True)

    results = run_benchmark()

    print("\nResults:", flush=True)
    total_time = sum(results.values())
    for name, duration in results.items():
        print(f"  {name}: {duration:.4f}s", flush=True)
    print(f"  TOTAL: {total_time:.4f}s", flush=True)
