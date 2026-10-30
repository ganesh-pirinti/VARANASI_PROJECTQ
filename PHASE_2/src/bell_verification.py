"""
src/bell_verification.py — Bell-State Verification on Processor D (Objective 1)
===========================================================================

Executes state preparation for |Phi+> = (|00> + |11>)/sqrt(2) on:
  1. Connected physical pair at distance 1: (0, 2)
  2. Maximally separated physical pair at distance 4: (0, 7)
Evaluates XX, YY, ZZ measurement bases with 4096 shots per basis under ideal
and official noisy simulation, computing correlations and fidelity with standard errors.

Covers all 12 measurement circuits:
  2 physical pairs x 2 noise conditions x 3 Pauli bases = 12 circuits.
"""

from __future__ import annotations
import os
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
from qiskit import transpile

from qff_phase2 import (
    bell_circuit,
    bell_experiment,
    load_processor,
    coupling_map_from_edges,
    simulator,
    parity_expectation,
    BASIS_GATES,
    OPT_LEVEL,
    SEED,
    SHOTS,
)


def run_bell_verification(
    processor_path: str = "processors/processor_D.json",
    near_pair: Tuple[int, int] = (0, 2),
    far_pair: Tuple[int, int] = (0, 7),
    output_csv_path: str = "results/tables/bell.csv",
    output_circuits_csv: str = "results/tables/bell_circuits.csv",
    output_raw_counts: str = "results/raw/bell_counts.json",
) -> List[dict]:
    """
    Run all 12 circuits (2 pairs x 2 conditions x 3 bases) and save summary and raw data.
    """
    proc = load_processor(processor_path)
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_raw_counts).parent.mkdir(parents=True, exist_ok=True)

    experiments = [
        ("near", near_pair, False),
        ("near", near_pair, True),
        ("far", far_pair, False),
        ("far", far_pair, True),
    ]

    cm = coupling_map_from_edges(proc["edges"], proc["num_qubits"])

    all_summary_rows = []
    circuit_rows = []
    raw_counts_dict = {}

    for ptype, pair, noisy in experiments:
        cond = "noisy" if noisy else "ideal"
        sim = simulator(noisy, proc)
        var = 0.0
        exp_record = {
            "processor": proc["name"],
            "pair": tuple(pair),
            "pair_type": ptype,
            "noisy": noisy,
            "condition": cond,
            "pair_distance": cm.distance(*pair),
            "shots": SHOTS,
        }

        for basis in ("XX", "YY", "ZZ"):
            tqc = transpile(
                bell_circuit(basis),
                basis_gates=BASIS_GATES,
                coupling_map=cm,
                initial_layout=list(pair),
                optimization_level=OPT_LEVEL,
                seed_transpiler=SEED,
            )
            job_result = sim.run(tqc, shots=SHOTS).result()
            counts = job_result.get_counts()
            e, se = parity_expectation(counts)
            exp_record[basis] = e
            exp_record[basis + "_se"] = se
            var += se ** 2

            cx_count = tqc.count_ops().get("cx", 0)
            if basis == "ZZ":
                exp_record["cx"] = cx_count

            circuit_key = f"{ptype}_{pair[0]}_{pair[1]}_{cond}_{basis}"
            raw_counts_dict[circuit_key] = counts

            circuit_rows.append({
                "circuit_id": len(circuit_rows) + 1,
                "circuit_key": circuit_key,
                "pair_type": ptype,
                "qubit_pair": f"({pair[0]},{pair[1]})",
                "distance": cm.distance(*pair),
                "condition": cond,
                "measurement_basis": basis,
                "cx_gates": cx_count,
                "shots": SHOTS,
                "correlator_value": round(e, 6),
                "correlator_se": round(se, 6),
            })

        exp_record["fidelity"] = (1.0 + exp_record["XX"] - exp_record["YY"] + exp_record["ZZ"]) / 4.0
        exp_record["fidelity_se"] = float(np.sqrt(var) / 4.0)
        all_summary_rows.append(exp_record)

    # Write summary bell.csv
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pair_type", "qubit_pair", "pair_distance", "condition", "cx_count",
            "exp_XX", "exp_XX_se", "exp_YY", "exp_YY_se", "exp_ZZ", "exp_ZZ_se",
            "fidelity", "fidelity_se", "shots"
        ])
        for r in all_summary_rows:
            writer.writerow([
                r["pair_type"],
                f"({r['pair'][0]},{r['pair'][1]})",
                r["pair_distance"],
                r["condition"],
                r.get("cx", 1),
                r["XX"],
                r["XX_se"],
                r["YY"],
                r["YY_se"],
                r["ZZ"],
                r["ZZ_se"],
                r["fidelity"],
                r["fidelity_se"],
                r["shots"],
            ])

    # Write per-circuit bell_circuits.csv (all 12 circuits)
    with open(output_circuits_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "circuit_id", "circuit_key", "pair_type", "qubit_pair", "distance",
            "condition", "measurement_basis", "cx_gates", "shots",
            "correlator_value", "correlator_se"
        ])
        writer.writeheader()
        writer.writerows(circuit_rows)

    # Write raw counts JSON
    with open(output_raw_counts, "w", encoding="utf-8") as f:
        json.dump(raw_counts_dict, f, indent=2)

    return all_summary_rows
