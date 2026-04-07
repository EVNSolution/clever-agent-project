#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


CONTEXT_REPO_NAME = "clever-context-monorepo"
CHANGE_REPO_NAME = "clever-change-control"

CONTEXT_DOCS = [
    "README.md",
    "docs/root/index.md",
    "docs/root/agent-runtime-governance.md",
    "docs/root/doc-governance.md",
    "docs/root/pipeline-governance.md",
    "docs/services/index.md",
    "docs/services/service-template.md",
]

CHANGE_DOCS = [
    "README.md",
    ".github/ISSUE_TEMPLATE/change-request.yml",
    ".github/ISSUE_TEMPLATE/rollback-request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
]


def run_command(cmd: list[str], cwd: Path | None = None) -> str | None:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return proc.stdout.strip()


def iter_ancestors(path: Path) -> Iterable[Path]:
    current = path.resolve()
    yield current
    yield from current.parents


def find_clever_root(start: Path) -> Path:
    for candidate in iter_ancestors(start):
        if (candidate / CONTEXT_REPO_NAME).is_dir() and (candidate / CHANGE_REPO_NAME).is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate CLEVER root containing both "
        f"{CONTEXT_REPO_NAME} and {CHANGE_REPO_NAME} from {start}"
    )


def find_git_root(start: Path) -> Path:
    output = run_command(["git", "-C", str(start), "rev-parse", "--show-toplevel"])
    if output:
        return Path(output).resolve()

    for candidate in iter_ancestors(start):
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(f"Could not locate git root from {start}")


def repo_full_name(repo_path: Path) -> str | None:
    remote = run_command(["git", "-C", str(repo_path), "remote", "get-url", "origin"])
    if not remote:
        return None

    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", remote)
    if not match:
        return None
    return f"{match.group('owner')}/{match.group('repo')}"


def build_project_start_title(purpose: str) -> str:
    if purpose and purpose != "needs-input":
        return purpose.splitlines()[0].strip()[:80]
    return "새 project-start 작업 시작"


def build_project_start_body(
    *,
    purpose: str,
    constraints: str,
    ui_impact: str,
    current_working_repo: str,
    target_repo: str,
    expected_result: str,
) -> str:
    return "\n".join(
        [
            "## Purpose",
            purpose,
            "",
            "## Constraints",
            constraints,
            "",
            "## Start Surface",
            f"- current working repo: {current_working_repo}",
            f"- target repo proposal: {target_repo}",
            f"- ui impact: {ui_impact}",
            "",
            "## Expected Result",
            expected_result,
            "",
            "## Requested Flow",
            "1. Review and approve this project-start draft.",
            "2. Create the project-start issue in clever-change-control.",
            "3. Use the created project-start issue number as the canonical identifier.",
            "4. Propose target repo creation or confirmation.",
            "5. Clone or pull the target repo locally.",
            "6. Continue in a new target-repo session.",
        ]
    ).strip()


def build_packet(
    *,
    user_session: str,
    current_working_repo: str,
    current_working_repo_path: str,
    target_repo: str,
    purpose: str,
    constraints: str,
    ui_impact: str,
    expected_result: str,
    ssot_docs_read: list[str],
    issue_repo: str = CHANGE_REPO_NAME,
) -> dict[str, Any]:
    requires_new_repo = target_repo != current_working_repo
    project_start_title = build_project_start_title(purpose)
    repo_bootstrap_proposal = (
        "After the project-start issue is approved and created, propose target repo "
        "creation or confirmation before cloning locally."
        if requires_new_repo
        else "After the project-start issue is approved and created, confirm the current "
        "repo is the target execution repo and refresh the local checkout."
    )
    handoff_summary = (
        f"Switch to the cloned target repo ({target_repo}) and continue in a new session "
        "for planning and implementation."
        if requires_new_repo
        else f"Continue in a fresh session scoped to the confirmed target repo "
        f"({target_repo}) after verifying the local checkout."
    )

    return {
        "user_session": user_session,
        "current_working_repo": current_working_repo,
        "current_working_repo_path": current_working_repo_path,
        "target_repo": target_repo,
        "purpose": purpose,
        "constraints": constraints,
        "ui_impact": ui_impact,
        "expected_result": expected_result,
        "ssot_docs_read": ssot_docs_read,
        "project_start_issue": {
            "issue_repo": issue_repo,
            "title": project_start_title,
            "status": "draft",
            "canonical_reference": "pending-project-start-issue",
            "approval_gate": "present-draft-and-wait-for-approval",
            "body": build_project_start_body(
                purpose=purpose,
                constraints=constraints,
                ui_impact=ui_impact,
                current_working_repo=current_working_repo,
                target_repo=target_repo,
                expected_result=expected_result,
            ),
        },
        "repo_bootstrap": {
            "source_repo": current_working_repo,
            "target_repo": target_repo,
            "requires_new_repo": requires_new_repo,
            "status": "proposed-after-approval",
            "proposal": repo_bootstrap_proposal,
            "post_create_clone": [
                "create-or-confirm target repo after project-start approval",
                "clone-or-pull the target repo locally",
                "verify local checkout is ready for follow-on work",
            ],
        },
        "repo_session_handoff": {
            "status": "recommended-after-clone",
            "recommended_session": "new-target-repo-session",
            "summary": handoff_summary,
        },
        "next_step": (
            "Present the project-start draft for approval. After approval, create the issue, "
            "propose repo bootstrap, clone or pull the target repo, and recommend a new "
            "target-repo session."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a CLEVER project-start bootstrap packet from the current repo."
    )
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory to inspect")
    parser.add_argument("--user-session", default=os.environ.get("USER", "unknown-session"))
    parser.add_argument("--target-repo")
    parser.add_argument("--purpose", default="needs-input")
    parser.add_argument("--constraints", default="needs-input")
    parser.add_argument("--ui-impact", default="unknown")
    parser.add_argument("--expected-result", default="needs-input")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    return parser.parse_args()


def build_ssot_docs(clever_root: Path) -> list[str]:
    context_repo_path = clever_root / CONTEXT_REPO_NAME
    change_repo_path = clever_root / CHANGE_REPO_NAME
    return [str(context_repo_path / rel) for rel in CONTEXT_DOCS] + [
        str(change_repo_path / rel) for rel in CHANGE_DOCS
    ]


def print_text_packet(packet: dict[str, Any]) -> None:
    print("BOOTSTRAP_PACKET_BEGIN")
    print(f"user-session: {packet['user_session']}")
    print(f"current-working-repo: {packet['current_working_repo']}")
    print(f"current-working-repo-path: {packet['current_working_repo_path']}")
    print(f"target-repo: {packet['target_repo']}")
    print(f"purpose: {packet['purpose']}")
    print(f"constraints: {packet['constraints']}")
    print(f"ui-impact: {packet['ui_impact']}")
    print(f"expected-result: {packet['expected_result']}")
    print("ssot-docs-read:")
    for item in packet["ssot_docs_read"]:
        print(f"- {item}")
    print(f"next-step: {packet['next_step']}")
    print("BOOTSTRAP_PACKET_END")
    print()

    project_start = packet["project_start_issue"]
    print("PROJECT_START_ISSUE_DRAFT_BEGIN")
    print(f"repo: {project_start['issue_repo']}")
    print(f"status: {project_start['status']}")
    print(f"canonical-reference: {project_start['canonical_reference']}")
    print(f"title: {project_start['title']}")
    print(project_start["body"])
    print("PROJECT_START_ISSUE_DRAFT_END")
    print()

    repo_bootstrap = packet["repo_bootstrap"]
    print("REPO_BOOTSTRAP_BEGIN")
    print(f"source-repo: {repo_bootstrap['source_repo']}")
    print(f"target-repo: {repo_bootstrap['target_repo']}")
    print(f"requires-new-repo: {'yes' if repo_bootstrap['requires_new_repo'] else 'no'}")
    print(f"status: {repo_bootstrap['status']}")
    print(f"proposal: {repo_bootstrap['proposal']}")
    print("post-create-clone:")
    for item in repo_bootstrap["post_create_clone"]:
        print(f"- {item}")
    print("REPO_BOOTSTRAP_END")
    print()

    handoff = packet["repo_session_handoff"]
    print("REPO_SESSION_HANDOFF_BEGIN")
    print(f"status: {handoff['status']}")
    print(f"recommended-session: {handoff['recommended_session']}")
    print(f"summary: {handoff['summary']}")
    print("REPO_SESSION_HANDOFF_END")


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    clever_root = find_clever_root(cwd)
    git_root = find_git_root(cwd)

    working_repo = git_root.name
    target_repo = args.target_repo or working_repo
    change_repo_path = clever_root / CHANGE_REPO_NAME
    packet = build_packet(
        user_session=args.user_session,
        current_working_repo=working_repo,
        current_working_repo_path=str(git_root),
        target_repo=target_repo,
        purpose=args.purpose,
        constraints=args.constraints,
        ui_impact=args.ui_impact,
        expected_result=args.expected_result,
        ssot_docs_read=build_ssot_docs(clever_root),
        issue_repo=repo_full_name(change_repo_path) or CHANGE_REPO_NAME,
    )

    if args.json:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
        return 0

    print_text_packet(packet)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
