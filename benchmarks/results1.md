 python3 run_benchmark.py

Detected Python Runtimes:
============================================================
  ✓ CPython (Python 3.12.6) - available
  ✓ PyPy (Python 3.10.14 (39dc8d3c85a7, Sep 14 2025, 13:02:08)
[PyPy 7.3.17 with GCC Apple LLVM 17.0.0 (clang-1700.3.19.1)]) - available
  ✓ UV (uv 0.9.27 (Homebrew 2026-01-26)) - available


======================================================================
BENCHMARK SUITE
======================================================================
Runtimes: python3, pypy, uv
Benchmarks: pure_python, numpy_scipy, mixed_io
Trials per benchmark: 3
Warmup runs: 2
======================================================================

======================================================================
MEASURING RUNTIME OVERHEAD
======================================================================

  Measuring python3 overhead...
    Import sys: 0.000001s
    Import os: 0.000001s
    Import time: 0.000000s
    Import json: 0.001253s

  Measuring pypy overhead...
    Import sys: 0.000006s
    Import os: 0.000002s
    Import time: 0.000001s
    Import json: 0.011456s

  Measuring uv overhead...
    Import sys: 0.000001s
    Import os: 0.000000s
    Import time: 0.000001s
    Import json: 0.001291s
    Import numpy: 0.038320s
    Import scipy: 0.051674s

======================================================================
RUNNING BENCHMARKS
======================================================================

**********************************************************************
BENCHMARK: pure_python
**********************************************************************

  Running pure_python on python3...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 6.4120s
      Trial 2/3: 6.5411s
      Trial 3/3: 6.2771s

    Result: 6.4100s ± 0.1078s

  Running pure_python on pypy...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 2.5790s
      Trial 2/3: 3.0856s
      Trial 3/3: 2.3789s

    Result: 2.6812s ± 0.2974s

  Running pure_python on uv...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 6.1722s
      Trial 2/3: 6.1497s
      Trial 3/3: 6.3315s

    Result: 6.2178s ± 0.0809s

**********************************************************************
BENCHMARK: numpy_scipy
**********************************************************************

  Running numpy_scipy on python3...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 0.0795s
      WARNING: Trial 1 failed with code 1
      Trial 2/3: 0.0725s
      WARNING: Trial 2 failed with code 1
      Trial 3/3: 0.0444s
      WARNING: Trial 3 failed with code 1

    Result: FAILED (return code 1)

  Running numpy_scipy on pypy...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 0.0458s
      WARNING: Trial 1 failed with code 1
      Trial 2/3: 0.0951s
      WARNING: Trial 2 failed with code 1
      Trial 3/3: 0.0354s
      WARNING: Trial 3 failed with code 1

    Result: FAILED (return code 1)

  Running numpy_scipy on uv...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 5.9908s
      Trial 2/3: 6.0116s
      Trial 3/3: 6.0690s

    Result: 6.0238s ± 0.0331s

**********************************************************************
BENCHMARK: mixed_io
**********************************************************************

  Running mixed_io on python3...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 209.9761s
      Trial 2/3: 208.0532s
      Trial 3/3: 201.0544s

    Result: 206.3612s ± 3.8338s

  Running mixed_io on pypy...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 140.4360s
      Trial 2/3: 133.2082s
      Trial 3/3: 142.2744s

    Result: 138.6396s ± 3.9132s

  Running mixed_io on uv...
    Running 2 warmup iterations...
      Warmup 1/2 complete
      Warmup 2/2 complete
    Running 3 timed trials...
      Trial 1/3: 69.3554s
      Trial 2/3: 74.2493s
      Trial 3/3: 66.3473s

    Result: 69.9840s ± 3.2565s

======================================================================
Results saved to: /Users/waqarm/Projects/python-runtime-benchmark/results/benchmark_results_20260127_120755.json
======================================================================

======================================================================
BENCHMARK SUMMARY
======================================================================

PURE_PYTHON:
----------------------------------------------------------------------
  pypy        :   2.6812s ± 0.2974s  (baseline)
  uv          :   6.2178s ± 0.0809s  (0.43x)
  python3     :   6.4100s ± 0.1078s  (0.42x)

NUMPY_SCIPY:
----------------------------------------------------------------------
  pypy        :   0.0587s ± 0.0261s  (baseline)
  python3     :   0.0655s ± 0.0152s  (0.90x)
  uv          :   6.0238s ± 0.0331s  (0.01x)

MIXED_IO:
----------------------------------------------------------------------
  uv          :  69.9840s ± 3.2565s  (baseline)
  pypy        : 138.6396s ± 3.9132s  (0.50x)
  python3     : 206.3612s ± 3.8338s  (0.34x)

======================================================================
