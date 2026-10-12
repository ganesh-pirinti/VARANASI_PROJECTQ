"""
Transpiler benchmarking and SWAP gate bottleneck analysis across official processor topologies.
Implements unified, single-lineage routing-stage instrumentation to guarantee metric consistency.

How Routing SWAPs Are Counted When Decomposed:
  In superconducting transmon architectures, hardware coupling maps constrain two-qubit
  interactions to nearest neighbors. Non-local interactions require inserting SWAP gates
  during layout and routing (e.g., SabreRouting). During subsequent synthesis (`BasisTranslator`),
  each explicit SWAP gate is canonically decomposed into three alternating CX gates:
      SWAP(u, v) = CX(u, v) . CX(v, u) . CX(u, v)
  Subsequent peephole optimization passes (e.g. `TwoQubitPeepholeOptimization`, `CommutativeCancellation`)
  can further cancel or consolidate CX pairs across commuting boundaries.
  The `RoutingStageInstrumenter` intercepts the compilation DAG in-flight after the routing stage
  and prior to basis translation, capturing the exact inserted SWAP count and intermediate circuit
  from the exact same execution lineage that produces the final physical circuit.

Methodological Consistency of Logical Baselines:
  To measure routing overhead fairly and scientifically without introducing optimization mismatch,
  for each optimization level L in {1, 2, 3}, a corresponding unconstrained baseline circuit is
  compiled into the target native basis without coupling map at the exact same optimization level L.
  Then:
      cx_overhead = physical_cx - logical_cx(level=L)
      routing_overhead_ratio = cx_overhead / logical_cx(level=L)
      depth_overhead = physical_depth - logical_depth(level=L)
"""

import json
import time
from typing import Dict, List, Any, Optional
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.converters import dag_to_circuit


class RoutingStageInstrumenter:
    """
    Instrumentation callback for Qiskit pass manager execution.
    Intercepts the transpilation DAG across compilation passes within a single
    compilation lineage to reliably record:
    1. The exact routing pass (e.g. SabreLayout, SabreRouting, BasicSwap, StochasticSwap)
       that inserted physical SWAP gates to satisfy coupling map constraints.
    2. The exact intermediate QuantumCircuit snapshot at that routing boundary
       prior to basis translation.
    """

    ROUTING_PASS_NAMES = {
        "SabreLayout",
        "SabreRouting",
        "BasicSwap",
        "LookaheadSwap",
        "StochasticSwap",
        "BipMapping",
    }

    def __init__(self):
        self.routing_swaps: int = 0
        self.routing_pass_name: Optional[str] = None
        self.routed_circuit: Optional[QuantumCircuit] = None
        self.observed_passes: List[str] = []
        self.instrumentation_ran: bool = False

    def __call__(self, pass_, dag, time, property_set, **kwargs):
        self.instrumentation_ran = True
        pname = pass_.name()
        self.observed_passes.append(pname)
        ops = dict(dag.count_ops())
        swaps = ops.get("swap", 0)

        # Intercept ONLY recognized layout/routing passes (no fallback to non-routing passes)
        if pname in self.ROUTING_PASS_NAMES:
            if swaps >= self.routing_swaps:
                self.routing_swaps = swaps
                self.routing_pass_name = pname
                self.routed_circuit = dag_to_circuit(dag)

    def validate(self) -> None:
        """
        Validate that routing instrumentation actually ran and that the captured
        circuit represents the intended routing stage.
        """
        if not self.instrumentation_ran:
            raise RuntimeError("RoutingStageInstrumenter did not run: no compiler passes were intercepted.")
        if self.routing_pass_name is None or self.routing_pass_name not in self.ROUTING_PASS_NAMES:
            raise RuntimeError(
                f"RoutingStageInstrumenter failed to observe an intended routing pass. "
                f"Observed passes: {self.observed_passes}"
            )
        if self.routed_circuit is None or not isinstance(self.routed_circuit, QuantumCircuit):
            raise RuntimeError("RoutingStageInstrumenter failed to capture a valid QuantumCircuit at the routing boundary.")

        # Ensure the captured circuit actually represents the routing stage
        captured_swaps = self.routed_circuit.count_ops().get("swap", 0)
        if captured_swaps != self.routing_swaps:
            raise RuntimeError(
                f"Captured circuit SWAP count ({captured_swaps}) does not match recorded routing SWAPs ({self.routing_swaps})."
            )


def validate_processor_config(config: Dict[str, Any]) -> None:
    """
    Validate processor configuration schema, coupling graph, and qubit indices.
    Catches missing vertices, invalid edges, duplicate edges, and asymmetric maps.
    """
    required_fields = ["processor_id", "num_qubits", "basis_gates", "coupling_map"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required processor configuration field: {field}")

    num_qubits = config["num_qubits"]
    if not isinstance(num_qubits, int) or num_qubits <= 0:
        raise ValueError(f"num_qubits must be a positive integer, got: {num_qubits}")

    coupling_map = config["coupling_map"]
    if not isinstance(coupling_map, list):
        raise ValueError("coupling_map must be a list of directed edge pairs.")

    seen_edges = set()
    for edge in coupling_map:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError(f"Invalid coupling edge format: {edge}")
        u, v = edge
        if not (0 <= u < num_qubits and 0 <= v < num_qubits):
            raise ValueError(
                f"Qubit index out of range in edge ({u}, {v}) for processor with {num_qubits} qubits."
            )
        if u == v:
            raise ValueError(f"Self-loop detected on qubit {u}.")
        edge_tuple = (u, v)
        if edge_tuple in seen_edges:
            raise ValueError(f"Duplicate edge detected in coupling map: {edge_tuple}")
        seen_edges.add(edge_tuple)

    # Ensure undirected symmetry in directed coupling map
    for u, v in seen_edges:
        if (v, u) not in seen_edges:
            raise ValueError(
                f"Asymmetric coupling map: edge ({u}, {v}) present but reverse ({v}, {u}) missing."
            )


def load_processor_config(filepath: str) -> Dict[str, Any]:
    """Load and validate processor coupling map and configuration from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        config = json.load(f)
    validate_processor_config(config)
    return config


def analyze_circuit_resources(circuit: QuantumCircuit) -> Dict[str, Any]:
    """Extract gate counts and depth from a QuantumCircuit."""
    op_counts = dict(circuit.count_ops())
    total_gates = sum(op_counts.values())
    depth = circuit.depth()
    cx_count = op_counts.get("cx", 0)
    swap_count = op_counts.get("swap", 0)
    single_qubit_gates = sum(v for k, v in op_counts.items() if k not in ["cx", "swap", "cz", "ecr"])
    two_qubit_gates = cx_count + swap_count + op_counts.get("cz", 0) + op_counts.get("ecr", 0)

    return {
        "op_counts": op_counts,
        "total_gates": total_gates,
        "depth": depth,
        "cx_count": cx_count,
        "swap_count": swap_count,
        "single_qubit_gates": single_qubit_gates,
        "two_qubit_gates": two_qubit_gates,
        "rz_count": op_counts.get("rz", 0),
        "sx_count": op_counts.get("sx", 0),
        "x_count": op_counts.get("x", 0),
    }


def benchmark_processor_transpilation(
    circuit: QuantumCircuit,
    processor_config: Dict[str, Any],
    instance_name: str = "Circuit",
    optimization_levels: List[int] = [1, 2, 3],
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Transpile a logical QAOA circuit onto a specified processor topology.
    
    Single-Lineage Instrumented Pipeline with Comparable Baselines:
      1. For each optimization level L in optimization_levels, generates an unconstrained
         no-coupling-map baseline at level L to ensure methodological consistency.
      2. Executes a single preset pass manager at level L on the target coupling map,
         instrumented with RoutingStageInstrumenter.
      3. Intercepts the DAG during layout/routing (capturing routing_pass and routing_swaps)
         before BasisTranslator decomposes SWAPs into 3 CX gates.
      
    This guarantees that SWAP counts, CX counts, depth, and routing overhead are
    measured from the exact same compilation lineage and compared against matched baselines.
    """
    validate_processor_config(processor_config)
    coupling_map = CouplingMap(processor_config["coupling_map"])
    native_basis = processor_config["basis_gates"]
    num_physical_qubits = processor_config["num_qubits"]
    circuit_qubits = circuit.num_qubits

    # Check physical qubit capacity constraint
    if circuit_qubits > num_physical_qubits:
        records = []
        for opt_level in optimization_levels:
            records.append({
                "instance": instance_name,
                "circuit_qubits": circuit_qubits,
                "processor_id": processor_config["processor_id"],
                "processor_qubits": num_physical_qubits,
                "label": processor_config["label"],
                "opt_level": opt_level,
                "status": "INFEASIBLE_CAPACITY_EXCEEDED",
                "graph_diameter": processor_config.get("graph_diameter"),
                "routing_pass": None,
                "logical_cx": None,
                "physical_cx": None,
                "cx_overhead": None,
                "routing_overhead_ratio": None,
                "routing_swaps": None,
                "physical_swaps": None,
                "logical_depth": None,
                "physical_depth": None,
                "depth_overhead": None,
                "total_gates": None,
                "single_qubit_gates": None,
                "two_qubit_gates": None,
                "active_qubits": None,
                "transpile_time_sec": None,
                "circuit_routed_physical": None,
                "circuit_routed_with_swaps": None,
                "error_note": f"Circuit requires {circuit_qubits} logical qubits, exceeding physical capacity ({num_physical_qubits})."
            })
        return records

    results = []

    for opt_level in optimization_levels:
        t0 = time.time()

        # Step 1: Unconstrained baseline (no coupling map) compiled at the MATCHING optimization level
        pm_logical = generate_preset_pass_manager(
            optimization_level=opt_level,
            basis_gates=native_basis,
            seed_transpiler=seed
        )
        logical_circuit = pm_logical.run(circuit)
        logical_res = analyze_circuit_resources(logical_circuit)
        logical_cx = logical_res["cx_count"]
        logical_depth = logical_res["depth"]

        # Step 2: Constrained compilation with RoutingStageInstrumenter callback
        pm = generate_preset_pass_manager(
            optimization_level=opt_level,
            coupling_map=coupling_map,
            basis_gates=native_basis,
            routing_method="sabre",
            layout_method="sabre",
            seed_transpiler=seed
        )
        instrumenter = RoutingStageInstrumenter()
        physical_circuit = pm.run(circuit, callback=instrumenter)
        instrumenter.validate()
        phys_time = time.time() - t0

        phys_res = analyze_circuit_resources(physical_circuit)
        routing_swaps = instrumenter.routing_swaps
        routing_pass_name = instrumenter.routing_pass_name
        routed_circuit = instrumenter.routed_circuit

        physical_cx = phys_res["cx_count"]
        physical_swaps = phys_res["swap_count"]  # 0 in native hardware basis
        cx_overhead = physical_cx - logical_cx
        depth_overhead = phys_res["depth"] - logical_depth
        routing_overhead_ratio = cx_overhead / logical_cx if logical_cx > 0 else 0.0

        results.append({
            "instance": instance_name,
            "circuit_qubits": circuit_qubits,
            "processor_id": processor_config["processor_id"],
            "processor_qubits": num_physical_qubits,
            "label": processor_config["label"],
            "opt_level": opt_level,
            "status": "COMPILED_SUCCESSFULLY",
            "graph_diameter": processor_config.get("graph_diameter"),
            "routing_pass": routing_pass_name,
            "logical_cx": logical_cx,
            "physical_cx": physical_cx,
            "cx_overhead": cx_overhead,
            "routing_overhead_ratio": routing_overhead_ratio,
            "routing_swaps": routing_swaps,
            "physical_swaps": physical_swaps,
            "logical_depth": logical_depth,
            "physical_depth": phys_res["depth"],
            "depth_overhead": depth_overhead,
            "total_gates": phys_res["total_gates"],
            "single_qubit_gates": phys_res["single_qubit_gates"],
            "two_qubit_gates": phys_res["two_qubit_gates"],
            "active_qubits": len(physical_circuit.qubits),
            "transpile_time_sec": phys_time,
            "circuit_routed_physical": physical_circuit,
            "circuit_routed_with_swaps": routed_circuit,
            "error_note": "None"
        })

    return results


def compile_comparison_dataframe(all_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """Compile benchmark records into a structured pandas DataFrame."""
    display_cols = [
        "instance",
        "circuit_qubits",
        "processor_id",
        "processor_qubits",
        "status",
        "opt_level",
        "physical_depth",
        "routing_swaps",
        "routing_pass",
        "physical_cx",
        "cx_overhead",
        "routing_overhead_ratio",
        "total_gates",
        "transpile_time_sec"
    ]
    df = pd.DataFrame(all_results)
    return df[display_cols]
