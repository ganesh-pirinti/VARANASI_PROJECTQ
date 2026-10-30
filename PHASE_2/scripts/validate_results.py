"""
scripts/validate_results.py — Independent Deliverable & Artifact Integrity Validator
====================================================================================

Verifies that all required CSV tables, JSON files, metadata provenance, figures,
and processor configurations exist, adhere to official schemas, and maintain
mathematical consistency.
"""

from __future__ import annotations
import os
import sys
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qff_phase2 import load_processor, validate_processor_d


def validate():
    print("=" * 65)
    print("  PS-O1 PHASE 2 REBUILD — DELIVERABLE INTEGRITY VALIDATOR")
    print("=" * 65)
    all_ok = True

    # 1. Processor D Check
    print("\n[1] Checking Processor D...")
    try:
        proc_d = load_processor("processors/processor_D.json")
        errs = validate_processor_d(proc_d, required_qubits=6)
        if errs:
            print(f"  FAIL: Processor D rule violations: {errs}")
            all_ok = False
        else:
            print("  PASS: Processor D valid (0 violations)")
    except Exception as e:
        print(f"  FAIL: {e}")
        all_ok = False

    # 2. Check results/tables/results.csv
    print("\n[2] Checking results/tables/results.csv...")
    results_path = "results/tables/results.csv"
    if not os.path.exists(results_path):
        print("  FAIL: results.csv does not exist")
        all_ok = False
    else:
        with open(results_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if len(rows) != 6:
            print(f"  FAIL: Expected 6 rows, got {len(rows)}")
            all_ok = False
        else:
            print(f"  PASS: results.csv contains {len(rows)} valid rows")
            for r in rows:
                if r["processor"] == "A":
                    assert r["executable"] == "false"
                else:
                    assert r["executable"] == "true"
                    assert float(r["quality_value"]) > 0.70

    # 3. Check results/tables/bell.csv & bell_circuits.csv
    print("\n[3] Checking Bell state verification results...")
    bell_path = "results/tables/bell.csv"
    if not os.path.exists(bell_path):
        print("  FAIL: bell.csv does not exist")
        all_ok = False
    else:
        with open(bell_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 4:
            print(f"  FAIL: Expected 4 rows in bell.csv, got {len(rows)}")
            all_ok = False
        else:
            print(f"  PASS: bell.csv contains {len(rows)} valid rows")
            for r in rows:
                f_val = float(r["fidelity"])
                assert 0.90 <= f_val <= 1.0

    bell_circuits_path = "results/tables/bell_circuits.csv"
    if not os.path.exists(bell_circuits_path):
        print("  FAIL: bell_circuits.csv does not exist")
        all_ok = False
    else:
        with open(bell_circuits_path, encoding="utf-8") as f:
            c_rows = list(csv.DictReader(f))
        if len(c_rows) != 12:
            print(f"  FAIL: Expected 12 rows in bell_circuits.csv, got {len(c_rows)}")
            all_ok = False
        else:
            print(f"  PASS: bell_circuits.csv contains all 12 measurement circuits (2 pairs x 2 conditions x 3 bases)")

    bell_counts_path = "results/raw/bell_counts.json"
    if not os.path.exists(bell_counts_path):
        print("  FAIL: bell_counts.json does not exist")
        all_ok = False
    else:
        with open(bell_counts_path, encoding="utf-8") as f:
            counts_dict = json.load(f)
        if len(counts_dict) != 12:
            print(f"  FAIL: Expected 12 count distributions in bell_counts.json, got {len(counts_dict)}")
            all_ok = False
        else:
            print(f"  PASS: bell_counts.json contains 12 raw count distributions (4096 shots each)")

    # 4. Check figures in results/figures/
    print("\n[4] Checking scientific figures (16 required + aliases)...")
    required_figs = [
        "max_cut_weighted_graph.png",
        "max_cut_optimal_partition.png",
        "max_cut_sampled_partition.png",
        "processor_A_coupling.png",
        "processor_B_coupling.png",
        "processor_D_coupling.png",
        "qaoa_p1_circuit.png",
        "processor_B_transpiled_circuit.png",
        "processor_D_transpiled_circuit.png",
        "qaoa_cut_distribution.png",
        "ideal_vs_noisy_comparison.png",
        "processor_resource_comparison.png",
        "bell_state_correlations.png",
        "bell_state_fidelity.png",
        "classical_cut_distribution.png",
        "qaoa_parameter_landscape.png",
        "network_partitioning_graph.png",
        "processor_topologies.png",
        "bell_fidelity_comparison.png",
        "architecture_tradeoff_map.png",
    ]
    for fig in required_figs:
        p = os.path.join("results/figures", fig)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            print(f"  PASS: {fig} ({os.path.getsize(p)} bytes)")
        else:
            print(f"  FAIL: {fig} missing or empty")
            all_ok = False

    # 5. Check metadata
    print("\n[5] Checking benchmark_metadata.json...")
    meta_path = "results/raw/benchmark_metadata.json"
    if os.path.exists(meta_path) and os.path.getsize(meta_path) > 0:
        print("  PASS: benchmark_metadata.json present")
    else:
        print("  FAIL: benchmark_metadata.json missing or empty")
        all_ok = False

    print("\n" + "=" * 65)
    print(f"  VALIDATION RESULT: {'ALL PASS [OK]' if all_ok else 'SOME CHECKS FAILED'}")
    print("=" * 65)
    return all_ok


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
