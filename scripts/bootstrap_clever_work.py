#!/usr/bin/env python3
"""Compatibility entrypoint for bootstrap helper.

Run this when you want to execute bootstrap from the repo root without
referring to the `.agent` directory directly.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    target = (
        root_dir
        / ".agent"
        / "skills"
        / "bootstrap-clever-work"
        / "scripts"
        / "bootstrap_clever_work.py"
    )
    if not target.exists():
        raise SystemExit("Unable to find bootstrap script: {0}".format(target))

    result = subprocess.run([sys.executable, str(target), *sys.argv[1:]], check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
