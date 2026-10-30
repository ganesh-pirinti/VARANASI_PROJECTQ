"""
tests/test_results_integrity.py — Schema & Consistency Tests for Artifacts
"""
import os
import csv
import json
import pytest
import nbformat


def test_results_csv_schema():
    path = "results/tables/results.csv"
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 6
    expected_headers = [
        "problem_id", "processor", "condition", "executable",
        "logical_qubits", "physical_qubits", "logical_cx", "cx",
        "depth", "two_q_depth", "swaps", "cx_overhead", "shots",
        "quality_metric", "quality_value", "p_opt", "classical_optimum",
        "random_baseline",
    ]
    assert reader.fieldnames == expected_headers


def test_bell_csv_schema():
    path = "results/tables/bell.csv"
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    for r in rows:
        fid = float(r["fidelity"])
        assert 0.90 <= fid <= 1.0


def test_bell_twelve_circuits_and_raw_counts():
    circuits_path = "results/tables/bell_circuits.csv"
    assert os.path.exists(circuits_path)
    with open(circuits_path, encoding="utf-8") as f:
        c_rows = list(csv.DictReader(f))
    assert len(c_rows) == 12, f"Expected 12 Bell measurement circuits, got {len(c_rows)}"
    expected_headers = [
        "circuit_id", "circuit_key", "pair_type", "qubit_pair", "distance",
        "condition", "measurement_basis", "cx_gates", "shots",
        "correlator_value", "correlator_se"
    ]
    for h in expected_headers:
        assert h in c_rows[0], f"Missing header {h} in bell_circuits.csv"

    counts_path = "results/raw/bell_counts.json"
    assert os.path.exists(counts_path)
    with open(counts_path, encoding="utf-8") as f:
        counts_dict = json.load(f)
    assert len(counts_dict) == 12, f"Expected 12 raw count distributions, got {len(counts_dict)}"
    for key, dist in counts_dict.items():
        assert sum(dist.values()) == 4096, f"Circuit {key} total shots != 4096"


def test_metadata_provenance():
    path = "results/raw/benchmark_metadata.json"
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        meta = json.load(f)
    assert "environment" in meta
    assert "hashes" in meta
    assert "classical_ground_truth" in meta


def test_optimization_runs_csv():
    import numpy as np
    path = "results/tables/optimization_runs.csv"
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
    for r in rows:
        s = int(r["seed"])
        expected_init = np.random.default_rng(s).uniform(0.0, np.pi, size=2)
        assert abs(float(r["initial_gamma"]) - expected_init[0]) < 1e-5
        assert abs(float(r["initial_beta"]) - expected_init[1]) < 1e-5
    best_row = max(rows, key=lambda r: float(r["approx_ratio"]))
    assert int(best_row["seed"]) == 3
    assert float(best_row["approx_ratio"]) > 0.80


def test_classical_enumeration_csv():
    path = "results/tables/classical_enumeration.csv"
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 64
    opt_rows = [r for r in rows if r["is_optimal"].lower() == "true"]
    assert len(opt_rows) == 2
    for r in opt_rows:
        assert int(r["cut_weight"]) == 22


def test_sixteen_figures_exist():
    fig_names = [
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
    ]
    for fn in fig_names:
        p = os.path.join("results/figures", fn)
        assert os.path.exists(p), f"Missing figure {fn}"
        assert os.path.getsize(p) > 0, f"Empty figure {fn}"


def test_main_notebook_clean_execution():
    nb_path = "main.ipynb"
    assert os.path.exists(nb_path)
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    assert len(code_cells) >= 6
    for idx, c in enumerate(code_cells):
        assert c.execution_count is not None, f"Code cell {idx+1} not executed"
        assert len(c.outputs) > 0, f"Code cell {idx+1} has no output"
        for out in c.outputs:
            assert out.output_type != "error", f"Code cell {idx+1} has error: {out.get('ename')}"
