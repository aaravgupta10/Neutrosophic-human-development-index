"""
Unified Replication Master Runner
Neutrosophic Human Development Index (HDI-N) Project

Executes the entire replication pipeline end-to-end:
1. Step 13: Full Population Composite Inputs & Operator Sensitivity Comparison
2. Step 14: Canonical Panel Construction (v1 and v2)
3. Step 14: Summary Statistics, North-South Disparities & Non-parametric Tests
4. Step 15: External Validation with Global Findex Indicators
5. Step 17: External Validation Six-Model Ladder OLS Regressions (HC3 Robust SEs)
6. Full Triple Aggregation & Rank Invariance Checks
7. Automated Test Suite Execution
"""

import sys
import time
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

def run_step(description, script_path):
    print("\n" + "=" * 75)
    print(f"RUNNING: {description}")
    print(f"Script: {script_path.relative_to(REPO_ROOT)}")
    print("=" * 75)
    start_time = time.time()
    res = subprocess.run([sys.executable, str(script_path)], cwd=str(REPO_ROOT), capture_output=True, text=True)
    duration = time.time() - start_time
    if res.returncode != 0:
        print(f"FAILED (Exit Code {res.returncode}) after {duration:.2f}s:")
        print(res.stderr)
        print(res.stdout)
        sys.exit(1)
    else:
        print(res.stdout.strip())
        print(f"--> COMPLETED in {duration:.2f}s")

def main():
    overall_start = time.time()
    print("*" * 75)
    print("NEUTROSOPHIC HUMAN DEVELOPMENT INDEX (HDI-N)")
    print("COMPLETE REPLICATION SUITE")
    print("*" * 75)

    scripts = [
        ("Step 13: Operator Sensitivity & Master Inputs", REPO_ROOT / "scripts" / "step13_compute.py"),
        ("Step 14: Canonical Panel Construction", REPO_ROOT / "scripts" / "step14_build.py"),
        ("Step 14: Canonical Statistics & Disparities", REPO_ROOT / "scripts" / "step14_statistics.py"),
        ("Step 15: Findex Validation Merge & Diagnostics", REPO_ROOT / "scripts" / "step15_validation.py"),
        ("Step 17: External Validation Horse-Race Estimation", REPO_ROOT / "scripts" / "step17_estimation.py"),
        ("Step 5: Full Triple Aggregation", REPO_ROOT / "scripts" / "full_triple_aggregation.py"),
    ]

    for desc, path in scripts:
        run_step(desc, path)

    print("\n" + "=" * 75)
    print("RUNNING AUTOMATED REPLICATION TESTS")
    print("=" * 75)
    test_res = subprocess.run(
        [sys.executable, "-m", "unittest", "tests/test_replication.py"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True
    )
    print(test_res.stdout)
    print(test_res.stderr)
    if test_res.returncode != 0:
        print("Replication tests failed!")
        sys.exit(1)

    total_time = time.time() - overall_start
    print("\n" + "*" * 75)
    print(f"ALL REPLICATION PIPELINES AND TESTS PASSED SUCCESSFULLY in {total_time:.2f}s!")
    print("*" * 75)

if __name__ == "__main__":
    main()
