"""
Mixed benchmark: Pure Python + NumPy/SciPy + Heavy I/O operations.
Tests combined compute and I/O performance with 5GB of data.
branchmark 1: Generate 5GB test data file
branchmark 2: Read and process 5GB file in chunks
branchmark 3: Write 5GB of processed data
branchmark 4: Mixed compute/I/O operations (100 cycles)
branchmark 5: Random access patterns (1000 seeks)
"""

import os
import sys
import time
import tempfile
import shutil

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("WARNING: NumPy not available", flush=True)
    NUMPY_AVAILABLE = False


def generate_test_data(file_path, size_gb=5):
    """Generate test data file of specified size."""
    print(f"  Generating {size_gb}GB test file...", flush=True)
    chunk_size = 100_000_000  # 100M elements at a time
    total_elements = (size_gb * 1024 * 1024 * 1024) // 8  # 8 bytes per float64
    chunks_needed = total_elements // chunk_size

    start = time.perf_counter()
    with open(file_path, 'wb') as f:
        for i in range(chunks_needed):
            if NUMPY_AVAILABLE:
                data = np.random.rand(chunk_size).astype(np.float64)
                f.write(data.tobytes())
            else:
                # Fallback to binary data if numpy not available
                data = os.urandom(chunk_size * 8)
                f.write(data)

            if (i + 1) % 10 == 0:
                progress = ((i + 1) / chunks_needed) * 100
                print(f"    Progress: {progress:.1f}%", flush=True)

    duration = time.perf_counter() - start
    actual_size = os.path.getsize(file_path) / (1024**3)
    print(f"    Generated {actual_size:.2f}GB in {duration:.4f}s", flush=True)
    return duration


def read_and_process_chunks(file_path):
    """Read file in chunks and perform computations."""
    print("  Reading and processing data in chunks...", flush=True)
    chunk_size = 100_000_000  # 100M elements
    bytes_per_chunk = chunk_size * 8
    results = []

    start = time.perf_counter()
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_bytes = f.read(bytes_per_chunk)
            if not chunk_bytes:
                break

            chunk_num += 1

            if NUMPY_AVAILABLE:
                # Convert to numpy array and process
                data = np.frombuffer(chunk_bytes, dtype=np.float64)

                # Perform computations
                mean_val = np.mean(data)
                std_val = np.std(data)
                max_val = np.max(data)
                min_val = np.min(data)

                # Some pure Python processing
                sum_squares = sum(x * x for x in data[:10000])

                results.append({
                    'mean': mean_val,
                    'std': std_val,
                    'max': max_val,
                    'min': min_val,
                    'sum_squares': sum_squares
                })
            else:
                # Fallback: just read the data
                results.append({'size': len(chunk_bytes)})

            if chunk_num % 10 == 0:
                print(f"    Processed {chunk_num} chunks", flush=True)

    duration = time.perf_counter() - start
    print(f"    Processed {chunk_num} chunks in {duration:.4f}s", flush=True)
    return duration, results


def write_processed_data(file_path, iterations=5):
    """Write large amounts of processed data."""
    print(f"  Writing processed data ({iterations} iterations)...", flush=True)
    chunk_size = 100_000_000

    start = time.perf_counter()
    for i in range(iterations):
        output_path = f"{file_path}.processed.{i}"
        with open(output_path, 'wb') as f:
            for j in range(10):  # Write 1GB per iteration
                if NUMPY_AVAILABLE:
                    # Generate and transform data
                    data = np.random.rand(chunk_size)
                    transformed = data * 2.0 + 1.0  # Simple transformation
                    squared = transformed ** 2
                    f.write(squared.tobytes())
                else:
                    data = os.urandom(chunk_size * 8)
                    f.write(data)

        # Clean up immediately to save space
        os.remove(output_path)

    duration = time.perf_counter() - start
    print(f"    Wrote and processed {iterations}GB in {duration:.4f}s", flush=True)
    return duration


def mixed_compute_io(data_size=1000000):
    """Mix computation with small I/O operations."""
    print("  Running mixed compute/I/O operations...", flush=True)
    start = time.perf_counter()

    temp_dir = tempfile.mkdtemp()
    try:
        for i in range(100):
            # Compute phase
            if NUMPY_AVAILABLE:
                data = np.random.rand(data_size)
                result = np.sum(data ** 2) / np.sqrt(np.sum(data ** 3) + 1)
            else:
                data = [float(x) / 1000 for x in range(min(data_size, 100000))]
                result = sum(x * x for x in data)

            # I/O phase
            file_path = os.path.join(temp_dir, f'temp_{i}.dat')
            with open(file_path, 'w') as f:
                f.write(f'{result}\n')

            # Read back and verify
            with open(file_path, 'r') as f:
                value = float(f.read().strip())

            os.remove(file_path)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    duration = time.perf_counter() - start
    print(f"    Completed 100 compute/I/O cycles in {duration:.4f}s", flush=True)
    return duration


def run_benchmark(data_dir):
    """Run all mixed benchmarks."""
    results = {}
    test_file = os.path.join(data_dir, 'test_data_5gb.bin')

    # Check if test file exists, if not generate it
    if not os.path.exists(test_file):
        print("Test data file not found, generating...", flush=True)
        results['data_generation'] = generate_test_data(test_file, size_gb=5)
    else:
        print(f"Using existing test data: {test_file}", flush=True)
        results['data_generation'] = 0.0

    # Benchmark 1: Read and process large file in chunks
    print("  Running: Read and process 5GB file...", flush=True)
    start = time.perf_counter()
    duration, processed_results = read_and_process_chunks(test_file)
    results['read_process'] = duration

    # Benchmark 2: Write large amounts of processed data
    print("  Running: Write processed data...", flush=True)
    results['write_process'] = write_processed_data(test_file, iterations=5)

    # Benchmark 3: Mixed compute and I/O
    print("  Running: Mixed compute/I/O...", flush=True)
    results['mixed_compute_io'] = mixed_compute_io(data_size=1_000_000)

    # Benchmark 4: Random access patterns
    print("  Running: Random access patterns...", flush=True)
    start = time.perf_counter()
    file_size = os.path.getsize(test_file)
    with open(test_file, 'rb') as f:
        if NUMPY_AVAILABLE:
            np.random.seed(42)
            positions = np.random.randint(0, file_size - 8000, size=1000)
            for pos in positions:
                f.seek(int(pos))
                data = f.read(8000)
                if len(data) == 8000:
                    arr = np.frombuffer(data, dtype=np.float64)
                    _ = np.mean(arr)
        else:
            # Simple random reads without numpy
            import random
            random.seed(42)
            for _ in range(1000):
                pos = random.randint(0, file_size - 8000)
                f.seek(pos)
                data = f.read(8000)

    results['random_access'] = time.perf_counter() - start
    print(f"    Completed 1000 random accesses in {results['random_access']:.4f}s")

    return results


if __name__ == "__main__":
    print("Mixed Heavy I/O Benchmark", flush=True)
    print("=" * 50, flush=True)

    # Use the test_data directory relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'test_data')
    os.makedirs(data_dir, exist_ok=True)

    results = run_benchmark(data_dir)

    print("\nResults:", flush=True)
    total_time = sum(v for k, v in results.items() if k != 'data_generation')
    for name, duration in results.items():
        if name == 'data_generation' and duration == 0:
            print(f"  {name}: (reused existing)", flush=True)
        else:
            print(f"  {name}: {duration:.4f}s", flush=True)
    print(f"  TOTAL (excluding data gen): {total_time:.4f}s", flush=True)
