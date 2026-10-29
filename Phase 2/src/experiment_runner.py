"""Automated Experiment Execution and Benchmark Pipeline for PS-O1.

Executes official benchmark runs across Processors A, B, and D under ideal and noisy
simulation, generating the official CSV tables and raw JSON artifacts.
"""
from __future__ import annotations
import os
import sys
import json
import csv
from typing import Dict, Any, List

# Re-export and wrap from benchmark_runner for backward compatibility
from src.benchmark_runner import run_all_benchmarks as _run_all_benchmarks
from src.bell_evaluator import run_bell_suite
from src.qaoa_solver import QAOASolver
from src.exact_solver import solve_exact_maxcut
from src.metrics import compute_histogram_metrics, calculate_bell_fidelity

def run_benchmarks(data_dir: str = "data", output_dir: str = "results") -> Dict[str, Any]:
    """Execute the full benchmark suite and ensure all tables and metadata exist."""
    return _run_all_benchmarks()

if __name__ == "__main__":
    print("Executing benchmark suite...")
    summary = run_benchmarks()
    print("Done! Results summary:")
    print(f"Classical optimum C* = {summary['ground_truth']['max_cut']}")
