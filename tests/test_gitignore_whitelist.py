from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_tracked_files_are_whitelisted_from_default_ignore():
    ls_files = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )

    blocked = []
    for path in ls_files.stdout.splitlines():
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "check-ignore",
                "--no-index",
                "-v",
                "--",
                path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if ignored.returncode != 0 or not ignored.stdout.strip():
            continue

        pattern = ignored.stdout.split("\t", 1)[0].rsplit(":", 1)[-1]
        if not pattern.startswith("!"):
            blocked.append(f"{path} matched {pattern}")

    assert blocked == []
