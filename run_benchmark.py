#!/usr/bin/env python3
"""
Main entry point for the Python Runtime Benchmark Suite.

Usage:
    python run_benchmark.py                    # Run all benchmarks on all runtimes
    python run_benchmark.py --runtimes python3 pypy  # Test specific runtimes
    python run_benchmark.py --benchmarks pure_python # Run specific benchmarks
    python run_benchmark.py --trials 5 --warmup 3    # Custom trial/warmup counts
"""

import sys
import os

# Add project root to path so we can import from runners package
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from runners.runner import main

if __name__ == "__main__":
    main()
