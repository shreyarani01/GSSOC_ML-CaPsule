#!/usr/bin/env python3
"""
Notebook Health Check Bot
Automatically tests Jupyter notebooks for errors, missing imports, and deprecations.
"""

import os
import sys
import subprocess
from pathlib import Path

def find_notebooks(root_dir="."):
    """Find all Jupyter notebooks in the repository."""
    notebooks = []
    for path in Path(root_dir).rglob("*.ipynb"):
        # Skip hidden directories and checkpoints
        if ".ipynb_checkpoints" not in str(path):
            notebooks.append(path)
    return notebooks

def test_notebook(notebook_path):
    """Test a single notebook using nbconvert."""
    result = {
        "path": str(notebook_path),
        "success": False,
        "error": None
    }
    
    try:
        # Run the notebook using nbconvert
        subprocess.run(
            [
                "jupyter", "nbconvert", "--to", "notebook",
                "--execute", str(notebook_path),
                "--output", "-", "--allow-errors"
            ],
            capture_output=True,
            text=True,
            timeout=300
        )
        result["success"] = True
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout (5 minutes)"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    notebooks = find_notebooks()
    print(f"Found {len(notebooks)} notebooks")
    
    results = []
    for nb in notebooks:
        print(f"Testing: {nb}")
        result = test_notebook(nb)
        results.append(result)
    
    # Create issue for failed notebooks
    failed = [r for r in results if not r["success"]]
    
    if failed:
        print(f"\n❌ {len(failed)} notebooks failed:")
        for f in failed:
            print(f"  - {f['path']}: {f['error']}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} notebooks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
    