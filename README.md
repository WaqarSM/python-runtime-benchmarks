# Python Runtime Benchmark Suite

A comprehensive benchmarking suite for comparing the performance of different Python runtimes: **CPython** (standard Python 3), **PyPy**, and **UV**.

## Features

- **Startup/Setup Time Measurement**: Measures cold start time and import overhead for each runtime
- **Multiple Benchmark Types**:
  1. **Pure Python Math**: Heavy computation using only Python builtins (primes, Fibonacci, matrix ops, Mandelbrot)
  2. **NumPy/SciPy Math**: Heavy computation with optimized libraries (matrix ops, FFT, linear algebra, optimization)
  3. **Mixed Heavy I/O**: Combined compute and I/O operations with 5GB data files
- **Statistical Analysis**: Multiple trials with warmup runs, calculates average, min, max, and standard deviation
- **Comprehensive Results**: JSON output with detailed metrics, human-readable summary

## Directory Structure

```
python-runtime-benchmark/
├── benchmarks/           # Benchmark implementations
│   ├── pure_python_math.py
│   ├── numpy_scipy_math.py
│   └── mixed_heavy_io.py
├── runners/              # Infrastructure for running benchmarks
│   ├── runner.py
│   ├── runtime_detector.py
│   └── timing_utils.py
├── results/              # Benchmark results (JSON files)
├── test_data/            # Test data for I/O benchmarks (5GB files)
├── run_benchmark.py      # Main entry point
├── requirements.txt
└── README.md
```

## Prerequisites

### Installing Runtimes

**CPython (Python 3)**:
```bash
# Usually pre-installed on macOS/Linux
python3 --version

# On Ubuntu/Debian
sudo apt-get install python3

# On macOS with Homebrew
brew install python3
```

**PyPy**:
```bash
# On Ubuntu/Debian
sudo apt-get install pypy3

# On macOS with Homebrew
brew install pypy3

# Or download from: https://www.pypy.org/download.html
```

**UV**:
```bash
# Install UV (Python package manager and runner)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Installing Dependencies

For CPython:
```bash
pip install -r requirements.txt
```

For PyPy (NumPy/SciPy may have limited support):
```bash
pypy3 -m pip install numpy scipy
```

For UV:
```bash
uv pip install -r requirements.txt
# Or let uv manage dependencies automatically
```

## Usage

### Basic Usage

Run all benchmarks on all available runtimes:
```bash
python3 run_benchmark.py
```

### Test Specific Runtimes

```bash
# Test only CPython and PyPy
python3 run_benchmark.py --runtimes python3 pypy

# Test only UV
python3 run_benchmark.py --runtimes uv
```

### Run Specific Benchmarks

```bash
# Run only pure Python benchmark
python3 run_benchmark.py --benchmarks pure_python

# Run NumPy/SciPy and mixed I/O benchmarks
python3 run_benchmark.py --benchmarks numpy_scipy mixed_io
```

### Customize Trial Count

```bash
# Run 5 trials with 3 warmup runs
python3 run_benchmark.py --trials 5 --warmup 3

# Quick test with 1 trial, no warmup
python3 run_benchmark.py --trials 1 --warmup 0
```

### Save Results with Custom Filename

```bash
python3 run_benchmark.py --output my_benchmark_results.json
```

### Combined Options

```bash
# Test PyPy on pure Python benchmark with 5 trials
python3 run_benchmark.py --runtimes pypy --benchmarks pure_python --trials 5
```

## Understanding Results

### Startup Time
- **Cold start**: Time from process creation to Python being ready
- **Import time**: Time to load standard library and external packages
- Important for understanding overhead, especially for short-running scripts

### Benchmark Metrics
- **Average**: Mean execution time across all trials
- **Min/Max**: Fastest and slowest runs
- **Std Dev**: Standard deviation showing consistency
- **Speedup**: Relative performance compared to fastest runtime (e.g., "2.5x" means 2.5 times faster)

### Expected Performance

**Pure Python Math**:
- **PyPy**: Typically 2-5x faster due to JIT compilation
- **CPython**: Baseline performance
- **UV**: Similar to CPython (uses CPython under the hood)

**NumPy/SciPy Math**:
- **CPython**: Usually fastest (optimized C extensions)
- **PyPy**: May be slower (limited NumPy optimization)
- **UV**: Similar to CPython

**Mixed Heavy I/O**:
- **Results vary**: I/O-bound portions similar across runtimes
- Compute portions follow patterns above
- Real-world workloads often fall into this category

## Output

Results are saved in two formats:

1. **JSON file** (`results/benchmark_results_YYYYMMDD_HHMMSS.json`):
   - Complete data with all trials
   - Runtime metadata (version, overhead)
   - Can be processed programmatically

2. **Terminal summary**:
   - Formatted table of results
   - Speedup comparisons
   - Easy to read at a glance

## Benchmark Details

### Pure Python Math
- Prime number generation (up to 50,000)
- Recursive Fibonacci (up to n=30)
- Iterative Fibonacci (up to n=10,000)
- 100x100 matrix multiplication in pure Python
- 800x600 Mandelbrot set calculation

### NumPy/SciPy Math
- 2000x2000 matrix multiplication
- FFT on 10M data points
- Eigenvalue decomposition (1000x1000)
- SVD decomposition (2000x1000)
- Statistics on 50M elements
- Function optimization (100 iterations)
- Numerical integration (10k iterations)
- Signal filtering (50 iterations)

### Mixed Heavy I/O
- Generate 5GB test data file (one-time)
- Read and process 5GB file in chunks
- Write 5GB of processed data
- Mixed compute/I/O operations (100 cycles)
- Random access patterns (1000 seeks)

## Tips

1. **Close other applications** before running benchmarks for consistent results
2. **PyPy warmup is critical**: First runs are slower, subsequent runs show true JIT performance
3. **I/O benchmarks are slow**: The mixed I/O benchmark can take 10+ minutes per runtime
4. **Disk space**: Ensure you have at least 10GB free for test data
5. **NumPy on PyPy**: May fail or be slow; this is expected and informative
6. **Run multiple times**: For publication-quality results, consider 5-10 trials

## Troubleshooting

**"Runtime not available"**:
- Ensure the runtime is installed and in your PATH
- Check with: `python3 --version`, `pypy3 --version`, `uv --version`

**NumPy/SciPy import errors on PyPy**:
- Expected behavior; PyPy has limited NumPy support
- Benchmark will be skipped automatically

**Timeout errors**:
- Increase timeout in `timing_utils.py` (default: 600 seconds)
- Or reduce benchmark size for testing

**Out of disk space**:
- The 5GB test file is created once and reused
- Remove `test_data/` directory to free space

## License

MIT License - Feel free to use and modify for your needs.

## Contributing

Contributions welcome! Consider adding:
- More benchmark types (networking, database, etc.)
- Additional runtimes (Pyston, GraalPy, etc.)
- Memory profiling integration
- Visualization of results (plots, charts)
- CI/CD integration examples
