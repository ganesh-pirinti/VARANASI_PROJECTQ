"""Comprehensive verification of benchmark CSVs, figures, and calculations."""
import csv
import os
import json

def verify_all():
    print("=== Step 1: results.csv Audit ===")
    r_path = "results/tables/results.csv"
    assert os.path.exists(r_path), f"{r_path} missing"
    with open(r_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    expected_fields = [
        "problem_id", "processor", "condition", "executable", "logical_qubits",
        "physical_qubits", "logical_cx", "cx", "depth", "two_q_depth",
        "swaps", "cx_overhead", "shots", "quality_metric", "quality_value",
        "p_opt", "classical_optimum", "random_baseline"
    ]
    assert fieldnames == expected_fields, f"Fieldnames mismatch: {fieldnames}"
    assert len(rows) == 6, f"Expected 6 rows, got {len(rows)}"

    # Check processor rows
    for r in rows:
        assert r["problem_id"] == "PS-O1"
        assert r["processor"] in ["A", "B", "D"]
        assert r["condition"] in ["ideal", "noisy"]
        assert r["classical_optimum"] == "22"
        assert r["random_baseline"] == "0.6136"
        if r["processor"] == "A":
            assert r["executable"] == "false"
            assert r["logical_qubits"] == "6"
            assert r["physical_qubits"] == "5"
            assert r["cx"] == ""
            assert r["quality_value"] == ""
        else:
            assert r["executable"] == "true"
            assert int(r["logical_cx"]) == 18
            assert int(r["shots"]) == 4096
            assert 0.75 <= float(r["quality_value"]) <= 0.85
            assert 0.10 <= float(r["p_opt"]) <= 0.16
            if r["processor"] == "B":
                assert int(r["cx"]) == 21
                assert int(r["swaps"]) == 1
                assert int(r["cx_overhead"]) == 3
                assert int(r["depth"]) == 37
                assert int(r["two_q_depth"]) == 17
            elif r["processor"] == "D":
                assert int(r["cx"]) == 18
                assert int(r["swaps"]) == 0
                assert int(r["cx_overhead"]) == 0
                assert int(r["depth"]) == 29
                assert int(r["two_q_depth"]) == 14
    print("results.csv verification: PASS (6 rows, all values within valid physical bounds)")

    print("\n=== Step 2: bell.csv Audit ===")
    b_path = "results/tables/bell.csv"
    assert os.path.exists(b_path), f"{b_path} missing"
    with open(b_path, "r", encoding="utf-8") as f:
        reader_b = csv.DictReader(f)
        b_fields = reader_b.fieldnames
        b_rows = list(reader_b)

    expected_b_fields = [
        "pair_type", "qubit_pair", "pair_distance", "condition", "cx_count",
        "exp_XX", "exp_XX_se", "exp_YY", "exp_YY_se", "exp_ZZ", "exp_ZZ_se",
        "fidelity", "fidelity_se", "shots"
    ]
    assert b_fields == expected_b_fields, f"Bell fieldnames mismatch: {b_fields}"
    assert len(b_rows) == 4, f"Expected 4 rows, got {len(b_rows)}"
    for r in b_rows:
        assert int(r["shots"]) == 4096
        f = float(r["fidelity"])
        se = float(r["fidelity_se"])
        if r["condition"] == "ideal":
            assert f == 1.0
            assert se == 0.0
        else:
            assert 0.93 <= f <= 0.98
            assert 0.0015 <= se <= 0.0035
        if r["pair_type"] == "near":
            assert r["qubit_pair"] == "(0,2)"
            assert int(r["pair_distance"]) == 1
            assert int(r["cx_count"]) == 1
        elif r["pair_type"] == "far":
            assert r["qubit_pair"] == "(0,7)"
            assert int(r["pair_distance"]) == 4
            assert int(r["cx_count"]) == 10
    print("bell.csv verification: PASS (4 rows, near & far pairs, ideal & noisy)")

    print("\n=== Step 3: Figures Audit ===")
    expected_figs = [
        "network_partitioning_graph.png",
        "processor_topologies.png",
        "bell_fidelity_comparison.png",
        "qaoa_cut_distribution.png",
        "processor_resource_comparison.png"
    ]
    for fig in expected_figs:
        fp = os.path.join("results/figures", fig)
        assert os.path.exists(fp), f"Figure {fig} missing"
        sz = os.path.getsize(fp)
        assert sz > 50000, f"Figure {fig} too small ({sz} bytes)"
        print(f"  {fig}: PASS ({sz} bytes)")

    print("\n=== Step 4: Processors Audit ===")
    for p_name, p_file, exp_n in [
        ("Processor A", "processors/processor_A.json", 5),
        ("Processor B", "processors/processor_B.json", 9),
        ("Processor D", "processors/processor_D.json", 9),
    ]:
        with open(p_file, "r") as f:
            p = json.load(f)
        assert p["name"] == p_name
        assert p["num_qubits"] == exp_n
        assert p["basis_gates"] == ["rz", "sx", "x", "cx"]
        print(f"  {p_name} ({p_file}): PASS")

    print("\n=== Step 5: Raw QAOA Histograms & Metadata Audit ===")
    counts_path = "results/raw/qaoa_counts.json"
    meta_path = "results/raw/benchmark_metadata.json"
    assert os.path.exists(counts_path), f"{counts_path} missing"
    assert os.path.exists(meta_path), f"{meta_path} missing"

    with open(counts_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    assert "runs" in raw_data
    assert len(raw_data["runs"]) == 4
    for r_key, r_val in raw_data["runs"].items():
        assert r_val["shots"] == 4096
        assert r_val["total_counts"] == 4096
        assert len(r_val["histogram"]) == 64
        assert r_val["best_sampled_cut"] == 22

    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
    assert meta_data["problem"]["problem_id"] == "PS-O1"
    assert meta_data["problem"]["graph"]["total_graph_weight"] == 27
    assert meta_data["classical_ground_truth"]["exact_maximum_cut"] == 22
    print("  results/raw/qaoa_counts.json: PASS")
    print("  results/raw/benchmark_metadata.json: PASS")

if __name__ == "__main__":
    verify_all()
