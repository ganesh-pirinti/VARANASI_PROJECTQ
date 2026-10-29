"""Copy Phase 2 deliverables to OneDrive destination and verify SHA-256 parity."""
import os
import shutil
import hashlib

src_root = r"C:\Projects\VARANASI_PROJECTQ\Phase 2"
dst_root = r"C:\Users\GANESH_PIRINTI\OneDrive\desktop\PROJECTQ_VARANASI\Phase 2"

os.makedirs(dst_root, exist_ok=True)

EXCLUDED = {
    "node_modules",
    "__pycache__",
    ".ipynb_checkpoints",
    ".backups",
    ".venv",
    "venv",
    ".pytest_cache",
    "evidence",
}

def should_skip(rel_p):
    parts = rel_p.replace("\\", "/").split("/")
    for p in parts:
        if p in EXCLUDED:
            return True
    return False

def hash_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

copied = 0
for root, dirs, files in os.walk(src_root):
    rel_dir = os.path.relpath(root, src_root)
    if should_skip(rel_dir):
        continue
    target_dir = os.path.join(dst_root, rel_dir) if rel_dir != "." else dst_root
    os.makedirs(target_dir, exist_ok=True)
    for fn in files:
        rel_f = os.path.join(rel_dir, fn) if rel_dir != "." else fn
        if should_skip(rel_f):
            continue
        src_f = os.path.join(src_root, rel_f)
        dst_f = os.path.join(dst_root, rel_f)
        shutil.copy2(src_f, dst_f)
        copied += 1

print(f"Copied {copied} files to {dst_root}")

critical_files = [
    "README.md",
    "report.md",
    "main.ipynb",
    "qff_phase2.py",
    "requirements.txt",
    "requirements-lock.txt",
    "instances.json",
    "data/instance.json",
    "data/studio_data.json",
    "processors/processor_A.json",
    "processors/processor_B.json",
    "processors/processor_D.json",
    "results/tables/results.csv",
    "results/tables/bell.csv",
    "results/tables/initializations.csv",
    "results/tables/resource_comparison.csv",
    "results/raw/qaoa_counts.json",
    "results/raw/benchmark_metadata.json",
    "docs/COMPLIANCE_MATRIX.md",
    "docs/SCIENTIFIC_LIMITATIONS.md",
    "docs/VARANASI_RESEARCH_AND_IMPLEMENTATION_REPORT.md",
    "presentation/VARANASI_Pitch_Deck.pptx",
    "presentation/VARANASI_Pitch_Deck.pdf",
    "dist/VARANASI_PS-O1_Phase2_Submission.zip"
]

all_match = True
for f in critical_files:
    s_p = os.path.join(src_root, f.replace("/", os.sep))
    d_p = os.path.join(dst_root, f.replace("/", os.sep))
    if not os.path.exists(s_p) or not os.path.exists(d_p):
        print(f"MISSING: {f}")
        all_match = False
        continue
    h_s = hash_file(s_p)
    h_d = hash_file(d_p)
    if h_s != h_d:
        print(f"MISMATCH: {f}")
        all_match = False
    else:
        print(f"MATCH: {f} ({h_s[:12]}...)")

print(f"Total critical files verified: {len(critical_files)}, All matched: {all_match}")
