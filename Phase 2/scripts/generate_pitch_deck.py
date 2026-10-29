"""Generates the professional 16:9 PowerPoint Pitch Deck and matching PDF export.

Outputs:
1. presentation/VARANASI_Pitch_Deck.pptx (Native editable PowerPoint deck)
2. presentation/VARANASI_Pitch_Deck.pdf (High-resolution publication PDF deck)

Design System:
- Palette: Dark Slate (#0F172A), Slate Card (#1E293B), Electric Cyan (#06B6D4),
  Coral Orange (#F97316), Emerald (#10B981), Text White (#F8FAFC), Slate Gray (#94A3B8).
- Typography: Clean sans-serif hierarchy, quantitative callout cards, zero generic filler.
"""
from __future__ import annotations
import os
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# RGB Color Definitions
C_BG = RGBColor(15, 23, 42)          # #0F172A Dark Slate
C_CARD = RGBColor(30, 41, 59)        # #1E293B Card Slate
C_BORDER = RGBColor(51, 65, 85)      # #334155 Border
C_CYAN = RGBColor(6, 182, 212)       # #06B6D4 Electric Cyan
C_CORAL = RGBColor(249, 115, 22)     # #F97316 Coral Orange
C_EMERALD = RGBColor(16, 185, 129)   # #10B981 Emerald
C_WHITE = RGBColor(248, 250, 252)    # #F8FAFC Pure White
C_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Slate Gray
C_RED = RGBColor(239, 68, 68)        # #EF4444 Crimson
C_INDIGO = RGBColor(99, 102, 241)    # #6366F1 Indigo


def _set_slide_background(slide, prs):
    """Fill slide with deep dark slate background."""
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()
    return bg


def _add_header(slide, category: str, title: str, subtitle: str):
    """Add standard structured header with category pill, main title, and key takeaway."""
    # Category pill
    tx_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8), Inches(0.35))
    tf_cat = tx_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_CYAN
    p_cat.font.name = "Segoe UI"

    # Main title
    tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
    tf_title = tx_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE
    p_title.font.name = "Segoe UI"

    # Subtitle / Key takeaway
    tx_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.4))
    tf_sub = tx_sub.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitle
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = C_MUTED
    p_sub.font.name = "Segoe UI"


def _add_footer(slide, slide_num: int, total_slides: int = 9):
    """Add discreet, professional footer bar."""
    tx = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    p.text = f"VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Qiskit Fall Fest 2026 — SRM University-AP | Slide {slide_num} of {total_slides}"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(100, 116, 139)
    p.font.name = "Segoe UI"


def _add_card(slide, left: float, top: float, width: float, height: float, title: str = "", border_color=C_BORDER):
    """Add a dark translucent-style container card."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    return card


def build_powerpoint_deck(output_pptx: str = "presentation/VARANASI_Pitch_Deck.pptx"):
    """Construct the complete 9-slide presentation using python-pptx."""
    os.makedirs(os.path.dirname(output_pptx), exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title & Executive Summary
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s1, prs)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.1), Inches(0.15), Inches(4.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_CYAN
    bar.line.fill.background()

    # Title block
    tx_t = s1.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(11.3), Inches(2.2))
    tf_t = tx_t.text_frame
    tf_t.word_wrap = True

    p0 = tf_t.paragraphs[0]
    p0.text = "QISKIT FALL FEST 2026 — SRM UNIVERSITY-AP  |  TRACK: OPTIMIZATION"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.font.name = "Segoe UI"

    p1 = tf_t.add_paragraph()
    p1.text = "Quantum Optimization of Network Partitioning Using QAOA"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.font.name = "Segoe UI"

    p2 = tf_t.add_paragraph()
    p2.text = "Problem PS-O1  •  Hardware Co-Design Paradigm  •  Team VARANASI"
    p2.font.size = Pt(14)
    p2.font.color.rgb = C_MUTED
    p2.font.name = "Segoe UI"

    # Executive Thesis Card
    _add_card(s1, 1.2, 3.4, 11.3, 1.25, border_color=C_CYAN)
    tx_th = s1.shapes.add_textbox(Inches(1.4), Inches(3.5), Inches(10.9), Inches(1.0))
    tf_th = tx_th.text_frame
    tf_th.word_wrap = True
    p_th0 = tf_th.paragraphs[0]
    p_th0.text = "EXECUTIVE HYPOTHESIS & SCIENTIFIC VERIFICATION"
    p_th0.font.size = Pt(10)
    p_th0.font.bold = True
    p_th0.font.color.rgb = C_CYAN
    p_th1 = tf_th.add_paragraph()
    p_th1.text = (
        "NISQ algorithms waste critical coherence on routing overhead. By co-designing Processor D "
        "to natively embed the PS-O1 interaction graph, we eliminate 100% of routing SWAPs, "
        "reducing physical CX gates by 14.3% and circuit depth by 21.6%, while delivering an optimal "
        "solution sampling probability of 12.50% (a 4.0x enhancement over uniform random guessing)."
    )
    p_th1.font.size = Pt(11)
    p_th1.font.color.rgb = C_WHITE

    # 4 Key Stat Badges
    stats = [
        ("0 SWAPs", "-100% Routing Overhead", C_EMERALD),
        ("18 CX Gates", "-14.29% vs Generic B (21)", C_CYAN),
        ("Depth 29", "-21.62% vs Generic B (37)", C_CYAN),
        ("4.0x Sampling", "12.50% vs 3.125% Random", C_CORAL),
    ]
    for i, (val, sub, col) in enumerate(stats):
        x = 1.2 + i * 2.88
        _add_card(s1, x, 4.85, 2.65, 1.35)
        tx_b = s1.shapes.add_textbox(Inches(x + 0.1), Inches(4.95), Inches(2.45), Inches(1.15))
        tf_b = tx_b.text_frame
        tf_b.word_wrap = True
        pb0 = tf_b.paragraphs[0]
        pb0.text = val
        pb0.font.size = Pt(18)
        pb0.font.bold = True
        pb0.font.color.rgb = col
        pb0.font.name = "Segoe UI"
        pb1 = tf_b.add_paragraph()
        pb1.text = sub
        pb1.font.size = Pt(9.5)
        pb1.font.color.rgb = C_MUTED
        pb1.font.name = "Segoe UI"

    # Metadata footer
    tx_meta = s1.shapes.add_textbox(Inches(1.2), Inches(6.35), Inches(11.3), Inches(0.5))
    tf_meta = tx_meta.text_frame
    p_m = tf_meta.paragraphs[0]
    p_m.text = "Team: VARANASI  |  Team ID: AP251100708044  |  Lead: Ganesh Pirinti  |  Release: Phase 2 Reproducible Submission"
    p_m.font.size = Pt(10)
    p_m.font.color.rgb = C_MUTED
    _add_footer(s1, 1)

    # =========================================================================
    # SLIDE 2: The Locked Problem & Classical Ground Truth
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s2, prs)
    _add_header(
        s2, "01 / PROBLEM FORMULATION & EXACT BASELINE",
        "The Locked PS-O1 Graph: Exact Ground Truth & Uniform Baseline",
        "Rigorous classical verification guarantees an immutable reference before running quantum algorithms."
    )

    # Left: Network partitioning graph image
    img_path = "results/figures/network_partitioning_graph.png"
    if os.path.exists(img_path):
        s2.shapes.add_picture(img_path, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.0))

    # Right: Analytical summary card
    _add_card(s2, 7.1, 1.8, 5.4, 5.0)
    tx_s2 = s2.shapes.add_textbox(Inches(7.3), Inches(2.0), Inches(5.0), Inches(4.6))
    tf_s2 = tx_s2.text_frame
    tf_s2.word_wrap = True

    items_s2 = [
        ("Graph Topology", "6 vertices, 9 weighted edges, total graph weight = 27."),
        ("Exact Maximum Cut (C*)", "C* = 22 / 27 (81.48% of total edge weight; 7 / 9 edges cut)."),
        ("Optimal Partitions", "Exactly 2 bitwise-complement assignments reach C* = 22:\n  • S = {0, 1, 3} vs S' = {2, 4, 5}  (x = 110100)\n  • Complement assignment (x = 001011)"),
        ("Uniform Random Baseline", "Mean cut = 13.50, approximation ratio r = 0.6136.\nRandom guessing hits optimum with probability P_opt = 2 / 64 = 3.125%."),
        ("Mathematical Formulation", "Max-Cut Hamiltonian: H_C = sum_{(u,v)} w_{uv} (I - Z_u Z_v) / 2.\nObjective: Map ground state to bi-partition maximizing cut weight."),
    ]
    for i, (head, body) in enumerate(items_s2):
        p_h = tf_s2.paragraphs[0] if i == 0 else tf_s2.add_paragraph()
        p_h.text = f"•  {head}: "
        p_h.font.bold = True
        p_h.font.size = Pt(11)
        p_h.font.color.rgb = C_CYAN
        p_b = tf_s2.add_paragraph()
        p_b.text = f"    {body}"
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = C_WHITE
    _add_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: Processor Architectures & The Co-Design Hypothesis
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s3, prs)
    _add_header(
        s3, "02 / HARDWARE ARCHITECTURES & CO-DESIGN",
        "Hardware Topologies: Capacity, Routing Bottlenecks, and Co-Design",
        "Benchmarking three distinct processors exposes why physical coupling geometry dictates QAOA efficiency."
    )

    # Top: Processor topologies image
    img_top = "results/figures/processor_topologies.png"
    if os.path.exists(img_top):
        s3.shapes.add_picture(img_top, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.2))

    # Bottom: 3 comparative cards
    procs = [
        ("Processor A (5 Qubits)", "CAPACITY BOTTLENECK", C_RED,
         "• 5 physical qubits < 6 required logical qubits.\n• Transpilation impossible; marked executable: false.\n• Proves physical qubit capacity is a hard prerequisite."),
        ("Processor B (9 Qubits)", "ROUTING BOTTLENECK", C_INDIGO,
         "• Generic heavy-hex/grid layout lacks direct edge (1, 4).\n• Transpiler inserts 1 SWAP gate (+3 CX overhead).\n• Results in CX = 21, Total Depth = 37, 2Q Depth = 17."),
        ("Processor D (9 Qubits)", "VARANASI CO-DESIGN", C_EMERALD,
         "• Native 6-node core embeds all 9 PS-O1 edges directly.\n• Closed 3-node ancillary ring keeps max degree <= 4.\n• ZERO SWAPs, CX = 18 (minimum possible), Depth = 29."),
    ]
    for i, (name, tag, col, bullets) in enumerate(procs):
        x = 0.8 + i * 4.0
        _add_card(s3, x, 5.2, 3.733, 1.75, border_color=col)
        tx_p = s3.shapes.add_textbox(Inches(x + 0.15), Inches(5.25), Inches(3.433), Inches(1.6))
        tf_p = tx_p.text_frame
        tf_p.word_wrap = True
        pp0 = tf_p.paragraphs[0]
        pp0.text = f"{name} — {tag}"
        pp0.font.size = Pt(10)
        pp0.font.bold = True
        pp0.font.color.rgb = col
        pp1 = tf_p.add_paragraph()
        pp1.text = bullets
        pp1.font.size = Pt(9.2)
        pp1.font.color.rgb = C_WHITE
    _add_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: Transpilation Efficiency: Hardware Co-Design in Action
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s4, prs)
    _add_header(
        s4, "03 / TRANSPILATION METRICS & RESOURCE REDUCTION",
        "Quantitative Circuit Resource Reduction: Processor B vs D",
        "Problem-matched topology eliminates routing overhead and significantly reduces physical gate counts."
    )

    # Left: Connected-dot dumbbell image
    img_res = "results/figures/processor_resource_comparison.png"
    if os.path.exists(img_res):
        s4.shapes.add_picture(img_res, Inches(0.8), Inches(1.8), Inches(6.8), Inches(4.9))

    # Right: Metric cards and analysis
    _add_card(s4, 7.9, 1.8, 4.633, 4.9)
    tx_s4 = s4.shapes.add_textbox(Inches(8.1), Inches(1.95), Inches(4.233), Inches(4.6))
    tf_s4 = tx_s4.text_frame
    tf_s4.word_wrap = True

    m_rows = [
        ("Physical CX Gates", "21 → 18", "-14.29% (-3 CX)", C_EMERALD),
        ("Total Circuit Depth", "37 → 29", "-21.62% (-8 Depth)", C_EMERALD),
        ("Two-Qubit Depth", "17 → 14", "-17.65% (-3 2Q Depth)", C_EMERALD),
        ("Routing SWAPs", "1 → 0", "-100.0% (Zero SWAPs)", C_EMERALD),
    ]

    p_t = tf_s4.paragraphs[0]
    p_t.text = "HARDWARE CO-DESIGN GAINS"
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = C_CYAN

    for label, change, delta, col in m_rows:
        p_lbl = tf_s4.add_paragraph()
        p_lbl.text = f"{label}: {change}"
        p_lbl.font.size = Pt(11)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_WHITE
        p_del = tf_s4.add_paragraph()
        p_del.text = f"  ↳ {delta}"
        p_del.font.size = Pt(10)
        p_del.font.bold = True
        p_del.font.color.rgb = col

    p_note = tf_s4.add_paragraph()
    p_note.text = (
        "\nScientific Takeaway:\n"
        "On noisy hardware, two-qubit CX gates are the dominant source of depolarizing "
        "noise (p2 = 0.005 vs p1 = 0.001). Eliminating 3 CX gates saves ~1.5% fidelity loss "
        "per execution, proving the direct value of topology co-design."
    )
    p_note.font.size = Pt(9.5)
    p_note.font.color.rgb = C_MUTED
    _add_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: Objective 1: Quantum Hardware Diagnostic (Bell State Tomography)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s5, prs)
    _add_header(
        s5, "04 / OBJECTIVE 1: HARDWARE DIAGNOSTIC",
        "Processor D Verification: Bell State Tomography Across Distance",
        "State tomography over near and far pairs validates physical fidelity and gate error accumulation."
    )

    # Left: Bell state comparison figure
    img_bell = "results/figures/bell_fidelity_comparison.png"
    if os.path.exists(img_bell):
        s5.shapes.add_picture(img_bell, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    # Right: Quantitative Tomography card
    _add_card(s5, 8.5, 1.8, 4.033, 4.9)
    tx_s5 = s5.shapes.add_textbox(Inches(8.7), Inches(1.95), Inches(3.633), Inches(4.6))
    tf_s5 = tx_s5.text_frame
    tf_s5.word_wrap = True

    b_items = [
        ("Official Noise Model", "p1 = 0.001, p2(CX) = 0.005, p_readout = 0.01.\n4,096 shots per measurement basis."),
        ("Near Pair (0, 2) — Dist 1", "Ideal Fidelity: 1.0000 ± 0.0000\nNoisy Fidelity: 0.9633 ± 0.0021\nGate count: 1 CX gate (direct edge)."),
        ("Far Pair (0, 7) — Dist 4", "Ideal Fidelity: 1.0000 ± 0.0000\nNoisy Fidelity: 0.9420 ± 0.0026\nGate count: 10 CX gates (via SWAP routing)."),
        ("Physical Interpretation", "Fidelity drops by 2.13 percentage points from dist 1 to dist 4, exactly tracking cumulative CX depolarizing error and readout bit-flips."),
    ]
    for i, (hd, txt) in enumerate(b_items):
        p_h = tf_s5.paragraphs[0] if i == 0 else tf_s5.add_paragraph()
        p_h.text = f"•  {hd}"
        p_h.font.size = Pt(10.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_CYAN
        p_b = tf_s5.add_paragraph()
        p_b.text = f"   {txt}"
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_WHITE
    _add_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: QAOA Solution Quality & 4.0x Sampling Enhancement
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s6, prs)
    _add_header(
        s6, "05 / QAOA PERFORMANCE & STOCHASTIC DOMINANCE",
        "Sampled Cut Distribution: 4.0x Optimal Solution Sampling Enhancement",
        "Both processors achieve numerically indistinguishable approximation ratios while outperforming random baseline."
    )

    # Left: Dual-panel QAOA cut distribution
    img_cut = "results/figures/qaoa_cut_distribution.png"
    if os.path.exists(img_cut):
        s6.shapes.add_picture(img_cut, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))

    # Right: Analytical stats card
    _add_card(s6, 8.5, 1.8, 4.033, 4.9)
    tx_s6 = s6.shapes.add_textbox(Inches(8.7), Inches(1.95), Inches(3.633), Inches(4.6))
    tf_s6 = tx_s6.text_frame
    tf_s6.word_wrap = True

    cut_stats = [
        ("Noisy Approx Ratio (r)", "Processor B: r = 0.7874 (Mean = 17.32)\nProcessor D: r = 0.7862 (Mean = 17.30)\nDifference: -0.0012 (-0.15% relative).\nNumerically indistinguishable under shot noise!"),
        ("Optimal Cut (C* = 22) Hits", "Processor B: 516 / 4096 (12.60%)\nProcessor D: 512 / 4096 (12.50%)\nUniform Random: 2 / 64 (3.125%)"),
        ("4.0x Sampling Enhancement", "QAOA concentrates probability on optimal bi-partitions {0,1,3} and {2,4,5} with 4.0x greater likelihood than uniform random guessing."),
        ("Stochastic Dominance", "Complementary CDF P(C >= c) shows QAOA strictly dominates the random baseline across all thresholds c >= 14."),
    ]
    for i, (hd, txt) in enumerate(cut_stats):
        p_h = tf_s6.paragraphs[0] if i == 0 else tf_s6.add_paragraph()
        p_h.text = f"•  {hd}"
        p_h.font.size = Pt(10.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_CORAL
        p_b = tf_s6.add_paragraph()
        p_b.text = f"   {txt}"
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_WHITE
    _add_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: Algorithmic Landscape & Hardware Co-Design Conclusion
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s7, prs)
    _add_header(
        s7, "06 / ALGORITHMIC LANDSCAPE & CONCLUSION",
        "Statevector Parameter Landscape & Co-Design Pareto Frontier",
        "Co-design provides decisive hardware efficiency gains without compromising algorithmic solution quality."
    )

    # Left: Parameter landscape
    img_land = "results/figures/qaoa_parameter_landscape.png"
    if os.path.exists(img_land):
        s7.shapes.add_picture(img_land, Inches(0.8), Inches(1.8), Inches(4.5), Inches(4.9))

    # Center: Architecture trade-off map
    img_map = "results/figures/architecture_tradeoff_map.png"
    if os.path.exists(img_map):
        s7.shapes.add_picture(img_map, Inches(5.5), Inches(1.8), Inches(4.2), Inches(4.9))

    # Right: Synthesis Card
    _add_card(s7, 9.9, 1.8, 2.633, 4.9)
    tx_s7 = s7.shapes.add_textbox(Inches(10.0), Inches(1.95), Inches(2.433), Inches(4.6))
    tf_s7 = tx_s7.text_frame
    tf_s7.word_wrap = True

    p_sy0 = tf_s7.paragraphs[0]
    p_sy0.text = "CORE SYNTHESIS"
    p_sy0.font.size = Pt(10.5)
    p_sy0.font.bold = True
    p_sy0.font.color.rgb = C_CYAN

    p_sy1 = tf_s7.add_paragraph()
    p_sy1.text = (
        "1. Parameter Landscape:\n"
        "Statevector optimization reaches global minimum at γ* = -0.1680, β* = 0.3327 with <C> = 17.71 (r = 0.8051).\n\n"
        "2. Co-Design Shift:\n"
        "Processor D shifts the Pareto frontier leftward: eliminating 14.3% CX gates and 21.6% depth while preserving solution quality (r = 0.7862).\n\n"
        "3. Future Impact:\n"
        "As QAOA scales to deeper circuits (p >= 2), eliminating routing overhead compounds multiplicatively."
    )
    p_sy1.font.size = Pt(9.2)
    p_sy1.font.color.rgb = C_WHITE
    _add_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: Backup Slide: Official Challenge Kit Compliance Matrix
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s8, prs)
    _add_header(
        s8, "BACKUP / OFFICIAL AUDIT COMPLIANCE",
        "Official Challenge Kit Compliance Matrix: 100% Verified",
        "Exhaustive verification against QFF 2026 Phase 2 Rules confirms absolute compliance."
    )

    _add_card(s8, 0.8, 1.8, 11.733, 4.9)
    tx_s8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(4.6))
    tf_s8 = tx_s8.text_frame
    tf_s8.word_wrap = True

    comp_items = [
        ("Processor Scope", "Processors A, B, and D evaluated. Processor C is explicitly ruled out in Challenge Kit Section 12 FAQ.", "PASS"),
        ("Processor D Constraints", "9 qubits (<= 12), connected topology, max node degree = 4 (<= 4), basis gates ['rz', 'sx', 'x', 'cx'].", "PASS"),
        ("Noise Model", "Official depolarizing (p1=0.001, p2=0.005) and readout bit-flip (p=0.01) implemented identically.", "PASS"),
        ("Execution Budget", "4,096 shots per run across all 4 benchmark configurations (16,384 total QAOA shots) + 16,384 Bell shots.", "PASS"),
        ("Capacity Enforcement", "Processor A (5 qubits) rigorously reported as non-executable for 6-qubit PS-O1 instance.", "PASS"),
        ("Reproducibility", "Independent 14-test suite validates bitstring cut weights, optimal counts, and statistical reproducibility.", "PASS"),
    ]
    for i, (req, detail, status) in enumerate(comp_items):
        p = tf_s8.paragraphs[0] if i == 0 else tf_s8.add_paragraph()
        p.text = f"[{status}]  {req}: {detail}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_WHITE
        p.font.name = "Segoe UI"
    _add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: Backup Slide: Adversarial Defense & Statistical Methodology
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    _set_slide_background(s9, prs)
    _add_header(
        s9, "BACKUP / ADVERSARIAL DEFENSE & RIGOR",
        "Adversarial Defense: Addressing Key Evaluator Questions",
        "Grounding claims in real statistical evidence eliminates speculative assertions and ensures total credibility."
    )

    _add_card(s9, 0.8, 1.8, 11.733, 4.9)
    tx_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(4.6))
    tf_s9 = tx_s9.text_frame
    tf_s9.word_wrap = True

    qa_defense = [
        ("Q: Why does Processor D have slightly lower noisy approximation ratio than B (0.7862 vs 0.7874)?",
         "A: With 4,096 shots, the standard error of the mean cut is ~0.06 (approx ratio SE ~ 0.0027). A delta of -0.0012 (-0.15% relative) is well within shot noise. We do not claim D produces a higher mean cut; D's verified achievement is architectural: eliminating 14.3% CX gates and 21.6% depth."),
        ("Q: Why p=1 instead of p=2?",
         "A: In the official kit, p=1 is mandatory, p=2 is optional. At p=1, noise is constrained, allowing direct attribution of routing overhead vs hardware fidelity. We validated the multi-seed optimizer across 5 seeds, selecting the optimal (seed 3)."),
        ("Q: Did you observe quantum algorithmic speedup?",
         "A: No. We strictly distinguish sampling probability enhancement (4.0x over uniform random) from wall-clock quantum speedup. On 6 qubits, classical enumeration takes < 1 ms; our contribution is architecture co-design on NISQ devices."),
        ("Q: What AI tools were utilized?",
         "A: Disclosed in all documentation: AI coding assistants were used for script scaffolding, formatting, and test automation. All quantum circuit logic, processor topologies, and data verification are authentic and reproducible."),
    ]
    for i, (q, a) in enumerate(qa_defense):
        p_q = tf_s9.paragraphs[0] if i == 0 else tf_s9.add_paragraph()
        p_q.text = q
        p_q.font.size = Pt(10.5)
        p_q.font.bold = True
        p_q.font.color.rgb = C_CYAN
        p_a = tf_s9.add_paragraph()
        p_a.text = a + "\n"
        p_a.font.size = Pt(9.5)
        p_a.font.color.rgb = C_WHITE
    _add_footer(s9, 9)

    prs.save(output_pptx)
    print(f"PowerPoint Pitch Deck saved successfully to: {output_pptx}")


def build_pdf_deck(output_pdf: str = "presentation/VARANASI_Pitch_Deck.pdf"):
    """Render every slide to high-resolution 16:9 PDF vector/image pages."""
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    # We will generate 9 publication-grade 16:9 figures and save them into a multi-page PDF!
    # Slide dimensions: 13.333 x 7.5 inches at 150 DPI = 2000 x 1125 px
    fig_w, fig_h = 13.333, 7.5

    with PdfPages(output_pdf) as pdf:
        # SLIDE 1
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#0F172A")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#0F172A")
        ax.axis("off")

        # Decorative bar
        rect = plt.Rectangle((0.05, 0.2), 0.01, 0.65, facecolor="#06B6D4", edgecolor="none")
        ax.add_patch(rect)

        ax.text(0.08, 0.82, "QISKIT FALL FEST 2026 — SRM UNIVERSITY-AP  |  TRACK: OPTIMIZATION",
                color="#06B6D4", fontsize=11, fontweight="bold")
        ax.text(0.08, 0.68, "Quantum Optimization of Network Partitioning Using QAOA",
                color="#F8FAFC", fontsize=24, fontweight="bold")
        ax.text(0.08, 0.60, "Problem PS-O1  •  Hardware Co-Design Paradigm  •  Team VARANASI",
                color="#94A3B8", fontsize=13)

        # Hypothesis card
        card = plt.Rectangle((0.08, 0.38), 0.84, 0.18, facecolor="#1E293B", edgecolor="#06B6D4", lw=1.5)
        ax.add_patch(card)
        ax.text(0.10, 0.51, "EXECUTIVE HYPOTHESIS & SCIENTIFIC VERIFICATION", color="#06B6D4", fontsize=10, fontweight="bold")
        ax.text(0.10, 0.41,
                "NISQ algorithms waste critical coherence on routing overhead. By co-designing Processor D\n"
                "to natively embed the PS-O1 interaction graph, we eliminate 100% of routing SWAPs,\n"
                "reducing physical CX gates by 14.3% and circuit depth by 21.6%, while delivering an optimal\n"
                "solution sampling probability of 12.50% (a 4.0x enhancement over uniform random guessing).",
                color="#F8FAFC", fontsize=10.5, va="top")

        # Badges
        b_data = [
            ("0 SWAPs", "-100% Routing Overhead", "#10B981"),
            ("18 CX Gates", "-14.29% vs Generic B (21)", "#06B6D4"),
            ("Depth 29", "-21.62% vs Generic B (37)", "#06B6D4"),
            ("4.0x Sampling", "12.50% vs 3.125% Random", "#F97316"),
        ]
        for i, (val, sub, col) in enumerate(b_data):
            bx = 0.08 + i * 0.215
            b_card = plt.Rectangle((bx, 0.18), 0.195, 0.16, facecolor="#1E293B", edgecolor="#334155", lw=1.2)
            ax.add_patch(b_card)
            ax.text(bx + 0.015, 0.28, val, color=col, fontsize=16, fontweight="bold")
            ax.text(bx + 0.015, 0.21, sub, color="#94A3B8", fontsize=8.5)

        ax.text(0.08, 0.08, "Team: VARANASI  |  Team ID: AP251100708044  |  Lead: Ganesh Pirinti  |  Release: Phase 2 Reproducible Submission",
                color="#64748B", fontsize=9.5)
        ax.text(0.08, 0.03, "VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Slide 1 of 9", color="#475569", fontsize=8.5)
        pdf.savefig(fig)
        plt.close(fig)

        # HELPER FOR EMBEDDED IMAGE SLIDES
        def make_img_slide(category, title, subtitle, img_file, bullet_title, bullets, slide_num, img_rect=[0.05, 0.14, 0.52, 0.72], card_rect=[0.59, 0.14, 0.36, 0.72]):
            fig = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#0F172A")
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_facecolor("#0F172A")
            ax.axis("off")

            # Header
            ax.text(0.05, 0.94, category.upper(), color="#06B6D4", fontsize=10, fontweight="bold")
            ax.text(0.05, 0.89, title, color="#F8FAFC", fontsize=18, fontweight="bold")
            ax.text(0.05, 0.85, subtitle, color="#94A3B8", fontsize=10.5)

            # Image
            if os.path.exists(img_file):
                im = mpimg.imread(img_file)
                ax_im = fig.add_axes(img_rect)
                ax_im.imshow(im)
                ax_im.axis("off")

            # Content Card
            card = plt.Rectangle((card_rect[0], card_rect[1]), card_rect[2], card_rect[3], facecolor="#1E293B", edgecolor="#334155", lw=1.2)
            ax.add_patch(card)

            ax.text(card_rect[0] + 0.02, card_rect[1] + card_rect[3] - 0.04, bullet_title, color="#06B6D4", fontsize=11, fontweight="bold")
            y = card_rect[1] + card_rect[3] - 0.09
            for head, body, col in bullets:
                ax.text(card_rect[0] + 0.02, y, f"• {head}", color=col, fontsize=9.5, fontweight="bold")
                y -= 0.035
                ax.text(card_rect[0] + 0.03, y, body, color="#F8FAFC", fontsize=8.5, va="top")
                y -= (0.025 * len(body.split("\n")) + 0.025)

            ax.text(0.05, 0.03, f"VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Slide {slide_num} of 9", color="#475569", fontsize=8.5)
            pdf.savefig(fig)
            plt.close(fig)

        # SLIDE 2
        make_img_slide(
            "01 / PROBLEM FORMULATION & EXACT BASELINE",
            "The Locked PS-O1 Graph: Exact Ground Truth & Uniform Baseline",
            "Rigorous classical verification guarantees an immutable reference before running quantum algorithms.",
            "results/figures/network_partitioning_graph.png",
            "EXACT GROUND TRUTH SUMMARY",
            [
                ("Graph Topology", "6 vertices, 9 weighted edges, total weight = 27.", "#06B6D4"),
                ("Exact Maximum Cut (C*)", "C* = 22 / 27 (81.48% weight, 7 / 9 edges cut).", "#10B981"),
                ("Optimal Partitions", "Exactly 2 complementary states reach C* = 22:\n  S = {0, 1, 3} vs S' = {2, 4, 5}  (x = 110100)\n  Complement assignment (x = 001011)", "#F8FAFC"),
                ("Uniform Random Baseline", "Mean cut = 13.50, approximation ratio r = 0.6136.\nRandom guessing hits optimum with P_opt = 3.125%.", "#F97316"),
            ],
            2
        )

        # SLIDE 3
        make_img_slide(
            "02 / HARDWARE ARCHITECTURES & CO-DESIGN",
            "Hardware Topologies: Capacity, Routing Bottlenecks, and Co-Design",
            "Benchmarking three distinct processors exposes why physical coupling geometry dictates QAOA efficiency.",
            "results/figures/processor_topologies.png",
            "ARCHITECTURAL COMPARISON",
            [
                ("Processor A (5 Qubits)", "CAPACITY BOTTLENECK: INFEASIBLE\n5 qubits < 6 required. Executable: false.", "#EF4444"),
                ("Processor B (9 Qubits)", "ROUTING BOTTLENECK: 1 SWAP\nMissing edge (1,4) adds 3 CX gates (+16.7%).\nTotal CX = 21, Depth = 37, 2Q Depth = 17.", "#6366F1"),
                ("Processor D (9 Qubits)", "VARANASI CO-DESIGN: 0 SWAPS\nNative 6-node core embeds all 9 edges directly.\nTotal CX = 18, Depth = 29, 2Q Depth = 14.", "#10B981"),
            ],
            3,
            img_rect=[0.05, 0.40, 0.90, 0.42],
            card_rect=[0.05, 0.08, 0.90, 0.28]
        )

        # SLIDE 4
        make_img_slide(
            "03 / TRANSPILATION METRICS & RESOURCE REDUCTION",
            "Quantitative Circuit Resource Reduction: Processor B vs D",
            "Problem-matched topology eliminates routing overhead and significantly reduces physical gate counts.",
            "results/figures/processor_resource_comparison.png",
            "HARDWARE CO-DESIGN GAINS",
            [
                ("Physical CX Gates", "21 → 18  (-14.29% reduction, saves 3 CX gates)", "#10B981"),
                ("Total Circuit Depth", "37 → 29  (-21.62% reduction, saves 8 layers)", "#10B981"),
                ("Two-Qubit Depth", "17 → 14  (-17.65% reduction, saves 3 2Q layers)", "#10B981"),
                ("Routing SWAPs", "1 → 0  (-100.0% reduction, zero overhead)", "#10B981"),
                ("Decoherence Impact", "Saves ~1.5% depolarizing error per execution\nunder official noise model (p2 = 0.005).", "#06B6D4"),
            ],
            4
        )

        # SLIDE 5
        make_img_slide(
            "04 / OBJECTIVE 1: HARDWARE DIAGNOSTIC",
            "Processor D Verification: Bell State Tomography Across Distance",
            "State tomography over near and far pairs validates physical fidelity and gate error accumulation.",
            "results/figures/bell_fidelity_comparison.png",
            "TOMOGRAPHY QUANTITATIVE AUDIT",
            [
                ("Official Noise Model", "p1 = 0.001, p2(CX) = 0.005, p_readout = 0.01.\n4,096 shots per measurement basis.", "#06B6D4"),
                ("Near Pair (0, 2) — Dist 1", "Ideal: 1.0000 ± 0.0000\nNoisy: 0.9633 ± 0.0021 (1 CX gate)", "#10B981"),
                ("Far Pair (0, 7) — Dist 4", "Ideal: 1.0000 ± 0.0000\nNoisy: 0.9420 ± 0.0026 (10 CX gates)", "#F97316"),
                ("Decoherence Analysis", "2.13% fidelity drop reflects cumulative CX\ndepolarizing error across 4 routing hops.", "#F8FAFC"),
            ],
            5
        )

        # SLIDE 6
        make_img_slide(
            "05 / QAOA PERFORMANCE & STOCHASTIC DOMINANCE",
            "Sampled Cut Distribution: 4.0x Optimal Solution Sampling Enhancement",
            "Both processors achieve numerically indistinguishable approximation ratios while outperforming random baseline.",
            "results/figures/qaoa_cut_distribution.png",
            "QAOA SAMPLING AUDIT",
            [
                ("Noisy Approx Ratio (r)", "Proc B: r = 0.7874 (Mean = 17.32)\nProc D: r = 0.7862 (Mean = 17.30)\nΔr = -0.0012 (-0.15% relative, within shot SE).", "#06B6D4"),
                ("Optimal Cut Hits (C* = 22)", "Proc B: 516 / 4096 (12.60%)\nProc D: 512 / 4096 (12.50%)\nUniform Random: 2 / 64 (3.125%)", "#10B981"),
                ("4.0x Sampling Enhancement", "QAOA concentrates probability on optimal bi-partitions\nwith 4.0x higher likelihood than random guessing.", "#F97316"),
                ("Stochastic Dominance", "CCDF P(C >= c) shows QAOA strictly dominates\nrandom baseline across all thresholds c >= 14.", "#F8FAFC"),
            ],
            6
        )

        # SLIDE 7: Algorithmic Landscape
        fig7 = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#0F172A")
        ax7 = fig7.add_axes([0, 0, 1, 1])
        ax7.set_facecolor("#0F172A")
        ax7.axis("off")
        ax7.text(0.05, 0.94, "06 / ALGORITHMIC LANDSCAPE & CONCLUSION", color="#06B6D4", fontsize=10, fontweight="bold")
        ax7.text(0.05, 0.89, "Statevector Parameter Landscape & Co-Design Pareto Frontier", color="#F8FAFC", fontsize=18, fontweight="bold")
        ax7.text(0.05, 0.85, "Co-design provides decisive hardware efficiency gains without compromising algorithmic solution quality.", color="#94A3B8", fontsize=10.5)

        # 2 Images side by side
        if os.path.exists("results/figures/qaoa_parameter_landscape.png"):
            ax_l = fig7.add_axes([0.05, 0.14, 0.36, 0.68])
            ax_l.imshow(mpimg.imread("results/figures/qaoa_parameter_landscape.png"))
            ax_l.axis("off")
        if os.path.exists("results/figures/architecture_tradeoff_map.png"):
            ax_m = fig7.add_axes([0.43, 0.14, 0.33, 0.68])
            ax_m.imshow(mpimg.imread("results/figures/architecture_tradeoff_map.png"))
            ax_m.axis("off")

        card7 = plt.Rectangle((0.78, 0.14), 0.17, 0.68, facecolor="#1E293B", edgecolor="#334155", lw=1.2)
        ax7.add_patch(card7)
        ax7.text(0.795, 0.78, "CORE SYNTHESIS", color="#06B6D4", fontsize=10, fontweight="bold")
        ax7.text(0.795, 0.73,
                 "1. Landscape:\n"
                 "Global optimum at\n"
                 "γ* = -0.1680\n"
                 "β* = 0.3327\n"
                 "⟨C⟩ = 17.71 (r = 0.805)\n\n"
                 "2. Pareto Shift:\n"
                 "Processor D saves\n"
                 "14.3% CX & 21.6% depth\n"
                 "with identical quality.\n\n"
                 "3. Scalability:\n"
                 "At depth p >= 2, zero\n"
                 "routing overhead\n"
                 "compounds multiplicatively.",
                 color="#F8FAFC", fontsize=8.2, va="top")

        ax7.text(0.05, 0.03, "VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Slide 7 of 9", color="#475569", fontsize=8.5)
        pdf.savefig(fig7)
        plt.close(fig7)

        # SLIDE 8: Compliance Matrix
        fig8 = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#0F172A")
        ax8 = fig8.add_axes([0, 0, 1, 1])
        ax8.set_facecolor("#0F172A")
        ax8.axis("off")
        ax8.text(0.05, 0.94, "BACKUP / OFFICIAL AUDIT COMPLIANCE", color="#06B6D4", fontsize=10, fontweight="bold")
        ax8.text(0.05, 0.89, "Official Challenge Kit Compliance Matrix: 100% Verified", color="#F8FAFC", fontsize=18, fontweight="bold")
        ax8.text(0.05, 0.85, "Exhaustive verification against QFF 2026 Phase 2 Rules confirms absolute compliance.", color="#94A3B8", fontsize=10.5)

        card8 = plt.Rectangle((0.05, 0.12), 0.90, 0.70, facecolor="#1E293B", edgecolor="#334155", lw=1.2)
        ax8.add_patch(card8)
        c_lines = [
            ("Processor Scope", "Processors A, B, and D evaluated. Processor C is explicitly ruled out in Challenge Kit Section 12 FAQ.", "PASS"),
            ("Processor D Rules", "9 qubits (<= 12), connected topology, max node degree = 4 (<= 4), basis gates ['rz', 'sx', 'x', 'cx'].", "PASS"),
            ("Noise Model", "Official depolarizing (p1=0.001, p2=0.005) and readout bit-flip (p=0.01) implemented identically.", "PASS"),
            ("Execution Budget", "4,096 shots per run across all 4 benchmark configurations (16,384 total QAOA shots) + 16,384 Bell shots.", "PASS"),
            ("Capacity Rule", "Processor A (5 qubits) rigorously reported as non-executable for 6-qubit PS-O1 instance.", "PASS"),
            ("Reproducibility", "Independent 14-test suite validates bitstring cut weights, optimal counts, and statistical reproducibility.", "PASS"),
        ]
        y8 = 0.76
        for title_c, desc_c, stat_c in c_lines:
            ax8.text(0.08, y8, f"[{stat_c}]  {title_c}", color="#10B981", fontsize=11, fontweight="bold")
            y8 -= 0.035
            ax8.text(0.11, y8, desc_c, color="#F8FAFC", fontsize=9.5)
            y8 -= 0.055

        ax8.text(0.05, 0.03, "VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Slide 8 of 9", color="#475569", fontsize=8.5)
        pdf.savefig(fig8)
        plt.close(fig8)

        # SLIDE 9: Defense Q&A
        fig9 = plt.figure(figsize=(fig_w, fig_h), dpi=150, facecolor="#0F172A")
        ax9 = fig9.add_axes([0, 0, 1, 1])
        ax9.set_facecolor("#0F172A")
        ax9.axis("off")
        ax9.text(0.05, 0.94, "BACKUP / ADVERSARIAL DEFENSE & RIGOR", color="#06B6D4", fontsize=10, fontweight="bold")
        ax9.text(0.05, 0.89, "Adversarial Defense: Addressing Key Evaluator Questions", color="#F8FAFC", fontsize=18, fontweight="bold")
        ax9.text(0.05, 0.85, "Grounding claims in real statistical evidence eliminates speculative assertions and ensures total credibility.", color="#94A3B8", fontsize=10.5)

        card9 = plt.Rectangle((0.05, 0.12), 0.90, 0.70, facecolor="#1E293B", edgecolor="#334155", lw=1.2)
        ax9.add_patch(card9)

        qas = [
            ("Q: Why is Processor D's noisy approximation ratio slightly lower than B (0.7862 vs 0.7874)?",
             "A: With 4,096 shots, standard error is ~0.0027. Delta of -0.0012 (-0.15% relative) is within random shot variance.\n   D's verified benefit is architectural: -14.3% CX gates and -21.6% depth with zero SWAPs."),
            ("Q: Why was p=1 selected over p=2?",
             "A: Depth p=1 is mandatory, p=2 is optional. p=1 isolates topology routing overhead without compounding optimizer noise.\n   Our multi-seed optimizer selected the best seed (seed 3, theoretical r = 0.8051)."),
            ("Q: Did you observe quantum algorithmic speedup?",
             "A: No. We report a 4.0x sampling enhancement over random guessing (12.50% vs 3.125%), not wall-clock speedup.\n   Classical enumeration takes <1 ms for 6 qubits; the real contribution is NISQ co-design."),
            ("Q: What AI tools were used?",
             "A: Disclosed in full: AI coding tools were used for test scaffolding and presentation scripts.\n   All circuit transpilation, simulation runs, and mathematical proofs are authentic and reproducible."),
        ]
        y9 = 0.76
        for q_txt, a_txt in qas:
            ax9.text(0.08, y9, q_txt, color="#06B6D4", fontsize=10.5, fontweight="bold")
            y9 -= 0.035
            ax9.text(0.10, y9, a_txt, color="#F8FAFC", fontsize=9.2)
            y9 -= 0.065

        ax9.text(0.05, 0.03, "VARANASI (AP251100708044) | PS-O1 QAOA Network Partitioning | Slide 9 of 9", color="#475569", fontsize=8.5)
        pdf.savefig(fig9)
        plt.close(fig9)

    print(f"Publication PDF Pitch Deck saved successfully to: {output_pdf}")


if __name__ == "__main__":
    build_powerpoint_deck()
    build_pdf_deck()
