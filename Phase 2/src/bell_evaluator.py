"""Bell-State Preparation, Measurement, and Verification on Processor D.

Executes |Phi+> = (|00> + |11>)/sqrt(2) state tomography across XX, YY, and ZZ
correlation bases for both adjacent (distance 1) and maximally distant (diameter)
qubit pairs, under ideal and noisy simulation.
Exports results to results/tables/bell.csv.
"""
from __future__ import annotations
import csv
import os
from typing import Dict, List, Tuple, Any

from qff_phase2 import (
    bell_experiment,
    load_processor,
    coupling_map_from_edges,
    SHOTS,
)

def run_bell_verification(
    processor_path: str = "processors/processor_D.json",
    near_pair: Tuple[int, int] = (0, 2),
    output_csv_path: str = "results/tables/bell.csv",
) -> List[Dict[str, Any]]:
    """Run full Bell state verification on Processor D and export to CSV.
    
    Pairs tested:
    1. Near pair: physical distance = 1 (directly connected edge)
    2. Far pair: physical distance = graph diameter (farthest pair)
    """
    proc = load_processor(processor_path)
    cm = coupling_map_from_edges(proc["edges"], proc["num_qubits"])
    
    # Identify farthest pair
    max_dist = 0
    far_pair = None
    for i in range(proc["num_qubits"]):
        for j in range(i + 1, proc["num_qubits"]):
            d = cm.distance(i, j)
            if d > max_dist:
                max_dist = d
                far_pair = (i, j)
                
    assert far_pair is not None, "Could not find far pair in processor graph"
    
    pairs = [
        ("near", near_pair, cm.distance(*near_pair)),
        ("far", far_pair, max_dist),
    ]
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    rows: List[Dict[str, Any]] = []
    
    for pair_label, pair, dist in pairs:
        for noisy in (False, True):
            res = bell_experiment(proc, physical_pair=pair, noisy=noisy, shots=SHOTS)
            condition_str = "noisy" if noisy else "ideal"
            
            row = {
                "pair_type": pair_label,
                "qubit_pair": f"({pair[0]},{pair[1]})",
                "pair_distance": dist,
                "condition": condition_str,
                "cx_count": res.get("cx", 0),
                "exp_XX": res["XX"],
                "exp_XX_se": res["XX_se"],
                "exp_YY": res["YY"],
                "exp_YY_se": res["YY_se"],
                "exp_ZZ": res["ZZ"],
                "exp_ZZ_se": res["ZZ_se"],
                "fidelity": res["fidelity"],
                "fidelity_se": res["fidelity_se"],
                "shots": SHOTS,
            }
            rows.append(row)
            
    # Write CSV
    fieldnames = [
        "pair_type",
        "qubit_pair",
        "pair_distance",
        "condition",
        "cx_count",
        "exp_XX",
        "exp_XX_se",
        "exp_YY",
        "exp_YY_se",
        "exp_ZZ",
        "exp_ZZ_se",
        "fidelity",
        "fidelity_se",
        "shots",
    ]
    
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
            
    return rows
