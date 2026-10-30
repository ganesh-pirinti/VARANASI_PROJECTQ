"""
scripts/package_submission.py — Submission Packaging & Verification
===================================================================

Packages the complete Phase 2 deliverable into:
  dist/QFF2026_PS-O1_Phase2_Submission.zip
and computes its external cryptographic checksum manifest:
  dist/QFF2026_PS-O1_Phase2_Submission.sha256

Validates the package via clean-extraction smoke testing (pytest & validator).
"""

from __future__ import annotations
import os
import sys
import zipfile
import hashlib
import tempfile
import subprocess
from pathlib import Path


def package_and_validate():
    base_dir = str(Path(__file__).resolve().parent.parent)
    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    zip_path = os.path.join(dist_dir, "QFF2026_PS-O1_Phase2_Submission.zip")
    sha_path = os.path.join(dist_dir, "QFF2026_PS-O1_Phase2_Submission.sha256")

    exclude_dirs = {"__pycache__", ".pytest_cache", ".git", ".qff2026-venv", "dist", ".ipynb_checkpoints"}
    exclude_exts = {".pyc", ".pyo"}

    print("=" * 70)
    print("  CREATING FINAL PHASE 2 SUBMISSION ZIP ARCHIVE")
    print("=" * 70)
    print(f"Target archive: {zip_path}")

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in exclude_exts or file.endswith("~"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                zipf.write(full_path, rel_path)
                file_count += 1

    size_bytes = os.path.getsize(zip_path)
    with open(zip_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    # Write external checksum manifest
    with open(sha_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256} *QFF2026_PS-O1_Phase2_Submission.zip\n")

    print("\nPackage Summary:")
    print(f"  Files included: {file_count}")
    print(f"  Archive Size:   {size_bytes:,} bytes ({size_bytes / 1024 / 1024:.2f} MB)")
    print(f"  SHA-256 Hash:   {sha256}")
    print(f"  External SHA:   {sha_path}")

    # Smoke test extraction in clean temp directory
    print("\n" + "-" * 70)
    print("  SMOKE TESTING: CLEAN-DIRECTORY EXTRACTION & VALIDATION")
    print("-" * 70)
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Extracting into temporary folder: {temp_dir}")
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(temp_dir)
        print("  Extraction complete.")

        python_exe = sys.executable

        # Run test suite from extracted package
        print("\n[Smoke Test 1/2] Running pytest from extracted package...")
        cmd_test = [python_exe, "-m", "pytest", "-v", "tests"]
        res_test = subprocess.run(cmd_test, capture_output=True, text=True, cwd=temp_dir)
        if res_test.returncode == 0:
            print("  PASS: Extracted automated test suite passed completely!")
        else:
            print(f"  FAIL: Extracted test suite failed:\n{res_test.stdout}\n{res_test.stderr}")
            sys.exit(1)

        # Run validate_results from extracted package
        print("\n[Smoke Test 2/2] Running validate_results.py from extracted package...")
        val_script = os.path.join(temp_dir, "scripts", "validate_results.py")
        res_val = subprocess.run([python_exe, val_script], capture_output=True, text=True, cwd=temp_dir)
        if res_val.returncode == 0:
            print("  PASS: Extracted validation script passed completely!")
        else:
            print(f"  FAIL: Validation script failed:\n{res_val.stdout}\n{res_val.stderr}")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("  ALL PACKAGE INTEGRITY & EXTRACTION CHECKS PASSED [SUCCESS]")
    print("=" * 70)
    return zip_path, size_bytes, sha256


if __name__ == "__main__":
    package_and_validate()
