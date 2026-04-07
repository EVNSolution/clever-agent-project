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
    "docs/wiki/index.md",
]

CHANGE_DOCS = [
    "README.md",
    ".github/ISSUE_TEMPLATE/project-start.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "changes",
    "releases",
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


def current_branch(repo_path: Path) -> str | None:
    return run_command(["git", "-C", str(repo_path), "branch", "--show-current"])


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


def repo_name(repo_path: Path) -> str:
    full_name = repo_full_name(repo_path)
    if full_name:
        return full_name.rsplit("/", 1)[-1]

    common_dir = run_command(
        ["git", "-C", str(repo_path), "rev-parse", "--path-format=absolute", "--git-common-dir"]
    )
    if common_dir:
        common_dir_path = Path(common_dir).resolve()
        if common_dir_path.name == ".git":
            return common_dir_path.parent.name
        return common_dir_path.name

    return find_git_root(repo_path).name


def is_checkout_root(path: Path) -> bool:
    output = run_command(["git", "-C", str(path), "rev-parse", "--show-toplevel"])
    return bool(output and Path(output).resolve() == path.resolve())


def list_git_worktrees(repo_path: Path) -> list[dict[str, str]]:
    output = run_command(["git", "-C", str(repo_path), "worktree", "list", "--porcelain"])
    if not output:
        return []

    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current["path"] = value
        elif key == "branch":
            current["branch"] = value.removeprefix("refs/heads/")
    if current:
        entries.append(current)
    return entries


def resolve_repo_checkout(
    *,
    clever_root: Path,
    repo_name_value: str,
    preferred_branch: str | None = None,
    preferred_checkout_name: str | None = None,
) -> Path:
    container = clever_root / repo_name_value
    candidates: list[Path] = [container]
    if preferred_checkout_name:
        candidates.append(container / preferred_checkout_name)
    child_candidates = (
        [child for child in sorted(container.iterdir()) if child.is_dir() and child.name != ".git"]
        if container.is_dir()
        else []
    )
    if preferred_branch and container.is_dir():
        for entry in list_git_worktrees(container):
            if entry.get("branch") != preferred_branch:
                continue
            worktree_path_value = entry.get("path")
            if not worktree_path_value:
                continue
            worktree_path = Path(worktree_path_value).resolve()
            if worktree_path.exists() and repo_name(worktree_path) == repo_name_value:
                return worktree_path
        repo_children = [
            child
            for child in child_candidates
            if is_checkout_root(child) and repo_name(child) == repo_name_value
        ]
        for child in repo_children:
            if current_branch(child) == preferred_branch:
                return child.resolve()
        if repo_children and not is_checkout_root(container):
            raise FileNotFoundError(
                f"Could not resolve checkout for {repo_name_value} on branch "
                f"{preferred_branch} from CLEVER root {clever_root}"
            )
    candidates.extend(child_candidates)

    seen: set[Path] = set()
    for candidate in candidates:
        resolved_candidate = candidate.resolve()
        if resolved_candidate in seen or not candidate.exists():
            continue
        seen.add(resolved_candidate)
        if not is_checkout_root(candidate):
            continue
        if repo_name(candidate) == repo_name_value:
            return resolved_candidate

    raise FileNotFoundError(
        f"Could not resolve checkout for {repo_name_value} from CLEVER root {clever_root}"
    )


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
    expected_result: str,
    target_repo_proposal: str,
    target_service_proposal: str,
    repo_bootstrap_proposal: str,
    canonical_linkage_expectations: str,
    repo_session_handoff: str,
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
            f"- target repo proposal: {target_repo_proposal}",
            f"- target service proposal: {target_service_proposal}",
            f"- ui impact: {ui_impact}",
            "",
            "## Expected Result",
            expected_result,
            "",
            "## Target Repo Proposal",
            target_repo_proposal,
            "",
            "## Target Service Proposal",
            target_service_proposal,
            "",
            "## Repo Bootstrap Proposal",
            repo_bootstrap_proposal,
            "",
            "## Canonical Linkage Expectations",
            canonical_linkage_expectations,
            "",
            "## Repo Session Handoff",
            repo_session_handoff,
        ]
    ).strip()


def build_packet(
    *,
    user_session: str,
    current_working_repo: str,
    current_working_repo_path: str,
    target_repo: str,
    target_repo_status: str,
    purpose: str,
    constraints: str,
    ui_impact: str,
    expected_result: str,
    ssot_docs_read: list[str],
    issue_repo: str = CHANGE_REPO_NAME,
) -> dict[str, Any]:
    requires_new_repo: bool | None
    if target_repo_status == "needs-confirmation":
        requires_new_repo = None
    else:
        requires_new_repo = target_repo != current_working_repo
    project_start_title = build_project_start_title(purpose)
    target_repo_proposal = (
        "deferred until approval; confirm which GitHub repo should be created or selected "
        "after the project-start issue exists."
        if target_repo_status == "needs-confirmation"
        else (
            f"proposed target repo: {target_repo}"
            if requires_new_repo
            else f"confirm the current working repo ({target_repo}) as the execution repo"
        )
    )
    target_service_proposal = (
        "deferred until repo bootstrap; target service is optional at project-start and "
        "should only be confirmed if it becomes necessary."
    )
    repo_bootstrap_proposal = (
        "After the project-start issue is approved and created, confirm the target repo "
        "before proposing repo creation or cloning."
        if target_repo_status == "needs-confirmation"
        else (
            "After the project-start issue is approved and created, propose target repo "
            "creation or confirmation before cloning locally."
            if requires_new_repo
            else "After the project-start issue is approved and created, confirm the current "
            "repo is the target execution repo and refresh the local checkout."
        )
    )
    canonical_linkage_expectations = "\n".join(
        [
            "- The created project-start issue number becomes the canonical identifier.",
            "- Child issues (`new`, `fix`, `change`, `refactoring`) must reference that "
            "project-start issue number.",
            "- Repo bootstrap records, pull requests, and follow-on planning should link "
            "back to the same project-start issue number instead of using a separate change id.",
        ]
    )
    handoff_summary = (
        "Confirm the target repo, prepare the local clone or pull step, and then continue "
        "in a fresh target-repo session."
        if target_repo_status == "needs-confirmation"
        else (
            f"Switch to the cloned target repo ({target_repo}) and continue in a new session "
            "for planning and implementation."
            if requires_new_repo
            else f"Continue in a fresh session scoped to the confirmed target repo "
            f"({target_repo}) after verifying the local checkout."
        )
    )

    return {
        "user_session": user_session,
        "current_working_repo": current_working_repo,
        "current_working_repo_path": current_working_repo_path,
        "target_repo": target_repo,
        "target_repo_status": target_repo_status,
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
                expected_result=expected_result,
                target_repo_proposal=target_repo_proposal,
                target_service_proposal=target_service_proposal,
                repo_bootstrap_proposal=repo_bootstrap_proposal,
                canonical_linkage_expectations=canonical_linkage_expectations,
                repo_session_handoff=handoff_summary,
            ),
        },
        "repo_bootstrap": {
            "source_repo": current_working_repo,
            "target_repo": target_repo,
            "target_repo_status": target_repo_status,
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


def build_ssot_docs(
    clever_root: Path,
    *,
    preferred_branch: str | None = None,
    preferred_checkout_name: str | None = None,
) -> list[str]:
    context_repo_path = resolve_repo_checkout(
        clever_root=clever_root,
        repo_name_value=CONTEXT_REPO_NAME,
        preferred_branch=preferred_branch,
        preferred_checkout_name=preferred_checkout_name,
    )
    change_repo_path = resolve_repo_checkout(
        clever_root=clever_root,
        repo_name_value=CHANGE_REPO_NAME,
        preferred_branch=preferred_branch,
        preferred_checkout_name=preferred_checkout_name,
    )
    return [str(context_repo_path / rel) for rel in CONTEXT_DOCS] + [
        str(change_repo_path / rel) for rel in CHANGE_DOCS
    ]


def print_text_packet(packet: dict[str, Any]) -> None:
    print("BOOTSTRAP_PACKET_BEGIN")
    print(f"user-session: {packet['user_session']}")
    print(f"current-working-repo: {packet['current_working_repo']}")
    print(f"current-working-repo-path: {packet['current_working_repo_path']}")
    print(f"target-repo: {packet['target_repo']} ({packet['target_repo_status']})")
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
    print(
        f"target-repo: {repo_bootstrap['target_repo']} "
        f"({repo_bootstrap['target_repo_status']})"
    )
    requires_new_repo = repo_bootstrap["requires_new_repo"]
    if requires_new_repo is None:
        print("requires-new-repo: needs-confirmation")
    else:
        print(f"requires-new-repo: {'yes' if requires_new_repo else 'no'}")
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
    branch_name = current_branch(git_root)

    working_repo = repo_name(git_root)
    if args.target_repo:
        target_repo = args.target_repo
        target_repo_status = "provided"
    else:
        target_repo = "needs-confirmation"
        target_repo_status = "needs-confirmation"
    change_repo_path = resolve_repo_checkout(
        clever_root=clever_root,
        repo_name_value=CHANGE_REPO_NAME,
        preferred_branch=branch_name,
        preferred_checkout_name=git_root.name,
    )
    packet = build_packet(
        user_session=args.user_session,
        current_working_repo=working_repo,
        current_working_repo_path=str(git_root),
        target_repo=target_repo,
        target_repo_status=target_repo_status,
        purpose=args.purpose,
        constraints=args.constraints,
        ui_impact=args.ui_impact,
        expected_result=args.expected_result,
        ssot_docs_read=build_ssot_docs(
            clever_root,
            preferred_branch=branch_name,
            preferred_checkout_name=git_root.name,
        ),
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
