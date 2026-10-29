"""Deterministic submission packager for VARANASI PS-O1 (Qiskit Fall Fest 2026).

Creates a clean, reproducible delivery archive:
- Consistent top-level root: VARANASI_PROJECTQ/
- Includes Phase 2 deliverables, raw experimental histograms, metadata, tests, tables, figures
- Preserves Phase One archive while stripping bytecode/caches
- Excludes .git, __pycache__, .pyc, .ipynb_checkpoints, virtual environments, local backups
- Generates MANIFEST.sha256 and MANIFEST.json containing cryptographic checksums for all files
- Verifies package extractability and checksum integrity
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

TOP_LEVEL_DIR = "Phase 2"
EXCLUDED_PATTERNS = [
    ".git",
    "__pycache__",
    ".ipynb_checkpoints",
    ".backups",
    ".venv",
    "venv",
    "dist",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    ".gemini",
    "evidence",
]

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".bak",
    ".zip",
}

def should_exclude(rel_path: str) -> bool:
    """Determine if a file or directory should be excluded from the delivery zip."""
    parts = Path(rel_path).parts
    for part in parts:
        for excl in EXCLUDED_PATTERNS:
            if part == excl or part.startswith(excl + "."):
                return True
    ext = os.path.splitext(rel_path)[1].lower()
    if ext in EXCLUDED_EXTENSIONS:
        return True
    return False

def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def collect_package_files(repo_root: str) -> list[str]:
    """Collect all files to include in the package, relative to repo_root."""
    included = []
    for root, dirs, files in os.walk(repo_root):
        # Filter directories in-place to prevent traversing excluded dirs
        dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), repo_root))]
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), repo_root).replace("\\", "/")
            if not should_exclude(rel):
                included.append(rel)
    included.sort()
    return included

def create_submission_package(
    repo_root: str = None,
    output_dir: str = None,
    archive_name: str = "VARANASI_PS-O1_Phase2_Submission.zip",
) -> str:
    """Create a clean, audited submission ZIP."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    phase2_dir = os.path.dirname(script_dir)
    
    if repo_root is None:
        repo_root = phase2_dir
    else:
        repo_root = os.path.abspath(repo_root)
        
    if output_dir is None:
        output_dir = os.path.join(phase2_dir, "dist")
    else:
        output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    zip_path = os.path.join(output_dir, archive_name)
    
    files = collect_package_files(repo_root)
    print(f"Collected {len(files)} files to package from {repo_root}")
    
    # Generate manifest records (excluding manifest files themselves)
    manifest_records = []
    manifest_txt_lines = []
    for rel in files:
        if rel in ("MANIFEST.sha256", "MANIFEST.json"):
            continue
        full_p = os.path.join(repo_root, rel)
        f_hash = compute_sha256(full_p)
        f_size = os.path.getsize(full_p)
        manifest_records.append({
            "path": f"{TOP_LEVEL_DIR}/{rel}",
            "relative_path": rel,
            "sha256": f_hash,
            "size_bytes": f_size,
        })
        manifest_txt_lines.append(f"{f_hash}  {TOP_LEVEL_DIR}/{rel}")
        
    manifest_txt_content = "\n".join(manifest_txt_lines) + "\n"
    manifest_json_content = json.dumps({
        "submission_package": archive_name,
        "team": "VARANASI",
        "participant_id": "AP251100708044",
        "problem_statement": "PS-O1",
        "total_files": len(manifest_records),
        "files": manifest_records,
    }, indent=2)
    
    # Write zip file deterministically
    print(f"Writing clean zip: {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Add manifest files first
        zf.writestr(f"{TOP_LEVEL_DIR}/MANIFEST.sha256", manifest_txt_content)
        zf.writestr(f"{TOP_LEVEL_DIR}/MANIFEST.json", manifest_json_content)
        
        for rel in files:
            full_p = os.path.join(repo_root, rel)
            arcname = f"{TOP_LEVEL_DIR}/{rel}"
            zf.write(full_p, arcname=arcname)
            
    zip_size = os.path.getsize(zip_path)
    print(f"Package created: {zip_path} ({zip_size:,} bytes, {len(files) + 2} entries including manifests)")
    
    # Verification: Test extraction into a temporary directory
    print("Verifying archive integrity and manifest checksums...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)
            
        extracted_root = os.path.join(tmp_dir, TOP_LEVEL_DIR)
        assert os.path.exists(extracted_root), "Top-level directory missing from archive"
        
        # Verify manifest checksums match extracted files
        manifest_file = os.path.join(extracted_root, "MANIFEST.json")
        assert os.path.exists(manifest_file), "MANIFEST.json missing from extracted archive"
        with open(manifest_file, "r", encoding="utf-8") as f_m:
            m_data = json.load(f_m)
            
        for item in m_data["files"]:
            extracted_path = os.path.join(tmp_dir, item["path"])
            assert os.path.exists(extracted_path), f"Extracted file missing: {item['path']}"
            actual_hash = compute_sha256(extracted_path)
            assert actual_hash == item["sha256"], f"Hash mismatch for {item['path']}: {actual_hash} vs {item['sha256']}"
            
    print("Archive integrity and manifest checksum verification: PASS!")
    return zip_path

if __name__ == "__main__":
    create_submission_package()
