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
START_REPO_NAME = "clever-agent-project"
CONTROL_PLANE_REPOS = (
    START_REPO_NAME,
    CONTEXT_REPO_NAME,
    CHANGE_REPO_NAME,
)
REPO_LOCAL_TASK_HINTS = {
    CONTEXT_REPO_NAME: (
        "current-repo-maintenance",
        "This session appears to be editing `clever-context-monorepo` itself. "
        "Stay in the current repository and treat it as the target for this session.",
    ),
    CHANGE_REPO_NAME: (
        "current-repo-maintenance",
        "This session appears to be editing `clever-change-control` itself. "
        "Stay in the current repository and treat it as the target for this session.",
    ),
}
ALLOWED_LIFECYCLE_ACTIONS = {
    "adopt",
    "modify",
    "migrate",
    "retire",
}
ALLOWED_UI_IMPACTS = {
    "unknown",
    "있음",
    "없음",
}

CONTEXT_DOCS = [
    "README.md",
    "docs/root/index.md",
    "docs/root/authority-boundaries.md",
    "docs/root/agent-runtime-governance.md",
    "docs/root/doc-governance.md",
    "docs/root/template-harness-governance.md",
    "docs/root/deploy-template-governance.md",
    "docs/root/pipeline-governance.md",
    "docs/templates/index.md",
]

CHANGE_DOCS = [
    "README.md",
    ".github/ISSUE_TEMPLATE/project-start.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "changes",
    "releases",
]

TARGET_REPO_SEED_FILES = [
    {
        "source_template": "clever-agent-project/docs/templates/target-repo-AGENTS.md",
        "destination": "AGENTS.md",
        "role": "agent execution procedure",
        "purpose": (
            "Define the order, method, checklists, and completion rules agents "
            "must follow in the target repo."
        ),
        "required_placeholders": [
            "project_start_issue",
            "change_control_issue",
            "target_repo",
            "target_service",
            "template_lineage",
            "default_work_branch",
        ],
    },
    {
        "source_template": "clever-agent-project/docs/templates/target-repo-project-brief.md",
        "destination": "docs/project-brief.md",
        "role": "project planning draft",
        "purpose": (
            "Capture the initial project intent, constraints, scope, and "
            "unresolved planning questions."
        ),
        "required_placeholders": [
            "project_start_issue",
            "target_repo",
            "target_service",
            "problem_statement",
            "expected_result",
            "constraints",
        ],
    },
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


def try_find_git_root(start: Path) -> Path | None:
    try:
        return find_git_root(start)
    except FileNotFoundError:
        return None


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


def try_repo_name(repo_path: Path | None) -> str | None:
    if repo_path is None:
        return None
    try:
        return repo_name(repo_path)
    except FileNotFoundError:
        return None


def is_checkout_root(path: Path) -> bool:
    output = run_command(["git", "-C", str(path), "rev-parse", "--show-toplevel"])
    return bool(output and Path(output).resolve() == path.resolve())


def infer_workspace_root(start: Path, git_root: Path | None = None) -> Path:
    seen: set[Path] = set()
    candidates: list[Path] = list(iter_ancestors(start))
    if git_root is not None:
        candidates.extend(iter_ancestors(git_root))

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if any((resolved / repo_name_value).exists() for repo_name_value in CONTROL_PLANE_REPOS):
            return resolved

    if git_root is not None:
        return git_root.parent.resolve()
    return start.resolve()


def probe_repo_checkout(
    *,
    clever_root: Path,
    repo_name_value: str,
    preferred_branch: str | None = None,
    preferred_checkout_name: str | None = None,
) -> Path | None:
    try:
        return resolve_repo_checkout(
            clever_root=clever_root,
            repo_name_value=repo_name_value,
            preferred_branch=preferred_branch,
            preferred_checkout_name=preferred_checkout_name,
        )
    except FileNotFoundError:
        direct = (clever_root / repo_name_value).resolve()
        if direct.exists() and is_checkout_root(direct):
            return direct
        return None


def build_workspace_check(start: Path, *, current_repo_maintenance: bool = False) -> dict[str, Any]:
    cwd = start.resolve()
    git_root = try_find_git_root(cwd)
    current_repo = try_repo_name(git_root)
    branch_name = current_branch(git_root) if git_root else None
    preferred_checkout_name = git_root.name if git_root else None
    clever_root = infer_workspace_root(cwd, git_root)

    repos: dict[str, dict[str, Any]] = {}
    missing_repositories: list[str] = []
    unresolved_repositories: list[str] = []
    for repo_name_value in CONTROL_PLANE_REPOS:
        direct_path = clever_root / repo_name_value
        resolved_checkout = probe_repo_checkout(
            clever_root=clever_root,
            repo_name_value=repo_name_value,
            preferred_branch=branch_name,
            preferred_checkout_name=preferred_checkout_name,
        )
        repo_state = {
            "directory_present": direct_path.exists(),
            "directory_path": str(direct_path),
            "checkout_resolved": resolved_checkout is not None,
            "checkout_path": str(resolved_checkout) if resolved_checkout else None,
        }
        repos[repo_name_value] = repo_state
        if not repo_state["directory_present"]:
            missing_repositories.append(repo_name_value)
        elif not repo_state["checkout_resolved"]:
            unresolved_repositories.append(repo_name_value)

    control_plane_complete = all(
        repos[repo_name_value]["checkout_resolved"] for repo_name_value in CONTROL_PLANE_REPOS
    )
    current_repo_is_start = current_repo == START_REPO_NAME
    repo_local_maintenance = current_repo_maintenance and current_repo in REPO_LOCAL_TASK_HINTS
    startup_ready = control_plane_complete and (current_repo_is_start or repo_local_maintenance)

    if not control_plane_complete:
        action = "stop-and-fix-workspace"
        message = (
            "CLEVER requires a local three-repository workspace: "
            "`clever-agent-project`, `clever-context-monorepo`, and `clever-change-control`. "
            "This workspace is incomplete, so startup interpretation and traceability are "
            "degraded."
        )
    elif repo_local_maintenance:
        action, message = REPO_LOCAL_TASK_HINTS[current_repo]
    elif not current_repo_is_start:
        action = "switch-to-clever-agent-project"
        message = (
            "The control-plane workspace is present, but startup should begin from "
            "`clever-agent-project`. Switch there before applying the first-response hard gate."
        )
    else:
        action = "proceed-with-hard-gate"
        message = (
            "The three-repository local workspace is ready. Start from "
            "`clever-agent-project` and continue with the first-response hard gate."
        )

    return {
        "cwd": str(cwd),
        "git_root": str(git_root) if git_root else None,
        "current_repo": current_repo,
        "current_branch": branch_name,
        "clever_root": str(clever_root),
        "control_plane_complete": control_plane_complete,
        "current_repo_is_start": current_repo_is_start,
        "current_repo_maintenance_requested": current_repo_maintenance,
        "repo_local_maintenance_candidate": repo_local_maintenance,
        "startup_ready": startup_ready,
        "missing_repositories": missing_repositories,
        "unresolved_repositories": unresolved_repositories,
        "recommended_start_repo": str(
            probe_repo_checkout(
                clever_root=clever_root,
                repo_name_value=START_REPO_NAME,
                preferred_branch=branch_name,
                preferred_checkout_name=preferred_checkout_name,
            )
            or (clever_root / START_REPO_NAME)
        ),
        "agent_action": action,
        "message": message,
        "repos": repos,
    }


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
    template_id: str,
    template_version: str,
    deploy_profile: str,
    override_scope: str,
    lifecycle_action: str,
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
            "## Template Harness",
            f"- template_id: {template_id}",
            f"- template_version: {template_version}",
            f"- deploy_profile: {deploy_profile}",
            f"- override_scope: {override_scope}",
            f"- lifecycle_action: {lifecycle_action}",
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


def build_target_repo_seed_files() -> list[dict[str, Any]]:
    return [dict(seed_file) for seed_file in TARGET_REPO_SEED_FILES]


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
    template_id: str,
    template_version: str,
    deploy_profile: str,
    override_scope: str,
    lifecycle_action: str,
    recorded_template_id: str | None = None,
    recorded_template_version: str | None = None,
    recorded_deploy_profile: str | None = None,
    issue_repo: str = CHANGE_REPO_NAME,
    workspace_check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if ui_impact not in ALLOWED_UI_IMPACTS:
        allowed = ", ".join(sorted(ALLOWED_UI_IMPACTS))
        raise ValueError(f"Unsupported ui_impact: {ui_impact}. Allowed: {allowed}")
    if lifecycle_action not in ALLOWED_LIFECYCLE_ACTIONS:
        allowed = ", ".join(sorted(ALLOWED_LIFECYCLE_ACTIONS))
        raise ValueError(f"Unsupported lifecycle_action: {lifecycle_action}. Allowed: {allowed}")
    if not re.fullmatch(r"[a-z0-9-]+", override_scope):
        raise ValueError(
            "override_scope must use lowercase letters, digits, and hyphen only."
        )
    if not re.fullmatch(r"[a-z0-9-]+", template_id):
        raise ValueError("template_id must use lowercase letters, digits, and hyphen only.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", template_version):
        raise ValueError(
            "template_version must use letters, digits, dot, underscore, or hyphen only."
        )
    if not re.fullmatch(r"[a-z0-9-]+", deploy_profile):
        raise ValueError(
            "deploy_profile must use lowercase letters, digits, and hyphen only."
        )
    lineage_differs = any(
        (
            recorded_template_id and recorded_template_id != template_id,
            recorded_template_version and recorded_template_version != template_version,
            recorded_deploy_profile and recorded_deploy_profile != deploy_profile,
        )
    )
    if lineage_differs and lifecycle_action != "migrate":
        raise ValueError(
            "Recorded template lineage differs from the selected template metadata. "
            "Use lifecycle_action=migrate."
        )

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
            "- The created project-start issue number becomes the root canonical identifier.",
            "- Child issues (`new`, `fix`, `change`, `refactoring`) must reference that "
            "project-start issue number.",
            "- Use change id only after approval, when a scoped change request, rollout, or "
            "rollback unit has been fixed.",
            "- Repo bootstrap records and pre-scope planning should link back to the same "
            "project-start issue number instead of inventing a change id early.",
        ]
    )
    handoff_summary = (
        "Confirm the target repo, prepare the local clone or pull step, seed AGENTS.md "
        "and docs/project-brief.md, and then continue in a fresh target-repo session."
        if target_repo_status == "needs-confirmation"
        else (
            f"Switch to the cloned target repo ({target_repo}), seed AGENTS.md and "
            "docs/project-brief.md, and continue in a new session for planning and "
            "implementation."
            if requires_new_repo
            else f"Continue in a fresh session scoped to the confirmed target repo "
            f"({target_repo}) after seeding AGENTS.md and docs/project-brief.md and "
            "verifying the local checkout."
        )
    )

    packet = {
        "user_session": user_session,
        "current_working_repo": current_working_repo,
        "current_working_repo_path": current_working_repo_path,
        "target_repo": target_repo,
        "target_repo_status": target_repo_status,
        "purpose": purpose,
        "constraints": constraints,
        "ui_impact": ui_impact,
        "expected_result": expected_result,
        "template_id": template_id,
        "template_version": template_version,
        "deploy_profile": deploy_profile,
        "override_scope": override_scope,
        "lifecycle_action": lifecycle_action,
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
                template_id=template_id,
                template_version=template_version,
                deploy_profile=deploy_profile,
                override_scope=override_scope,
                lifecycle_action=lifecycle_action,
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
                "copy target repo seed files before handoff",
                "verify local checkout is ready for follow-on work",
            ],
        },
        "target_repo_seed_files": build_target_repo_seed_files(),
        "repo_session_handoff": {
            "status": "recommended-after-clone",
            "recommended_session": "new-target-repo-session",
            "summary": handoff_summary,
        },
        "next_step": (
            "Present the project-start draft for approval. After approval, create the issue, "
            "propose repo bootstrap, clone or pull the target repo, seed the target repo, "
            "and recommend a new target-repo session."
        ),
    }
    if workspace_check is not None:
        packet["workspace_check"] = workspace_check
    return packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a CLEVER project-start bootstrap packet from the current repo."
    )
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory to inspect")
    parser.add_argument("--user-session", default=os.environ.get("USER", "unknown-session"))
    parser.add_argument(
        "--workspace-check",
        action="store_true",
        help="Inspect the local three-repository workspace and report startup readiness.",
    )
    parser.add_argument(
        "--current-repo-maintenance",
        action="store_true",
        help="Treat the current control-plane repo as the intended maintenance target.",
    )
    parser.add_argument("--target-repo")
    parser.add_argument("--purpose", default="needs-input")
    parser.add_argument("--constraints", default="needs-input")
    parser.add_argument("--ui-impact", default="unknown", choices=sorted(ALLOWED_UI_IMPACTS))
    parser.add_argument("--expected-result", default="needs-input")
    parser.add_argument("--template-id")
    parser.add_argument("--template-version")
    parser.add_argument("--deploy-profile")
    parser.add_argument("--override-scope")
    parser.add_argument(
        "--lifecycle-action",
        choices=sorted(ALLOWED_LIFECYCLE_ACTIONS),
    )
    parser.add_argument("--recorded-template-id")
    parser.add_argument("--recorded-template-version")
    parser.add_argument("--recorded-deploy-profile")
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


def print_workspace_check(workspace_check: dict[str, Any]) -> None:
    print("WORKSPACE_CHECK_BEGIN")
    print(f"cwd: {workspace_check['cwd']}")
    print(f"git-root: {workspace_check['git_root']}")
    print(f"current-repo: {workspace_check['current_repo']}")
    print(f"clever-root: {workspace_check['clever_root']}")
    print(
        "control-plane-complete: "
        f"{'yes' if workspace_check['control_plane_complete'] else 'no'}"
    )
    print(f"current-repo-is-start: {'yes' if workspace_check['current_repo_is_start'] else 'no'}")
    print(f"startup-ready: {'yes' if workspace_check['startup_ready'] else 'no'}")
    print(f"agent-action: {workspace_check['agent_action']}")
    print(f"message: {workspace_check['message']}")
    if workspace_check["missing_repositories"]:
        print("missing-repositories:")
        for item in workspace_check["missing_repositories"]:
            print(f"- {item}")
    if workspace_check["unresolved_repositories"]:
        print("unresolved-repositories:")
        for item in workspace_check["unresolved_repositories"]:
            print(f"- {item}")
    print(f"recommended-start-repo: {workspace_check['recommended_start_repo']}")
    print("WORKSPACE_CHECK_END")


def print_text_packet(packet: dict[str, Any]) -> None:
    workspace_check = packet.get("workspace_check")
    if workspace_check:
        print_workspace_check(workspace_check)
        print()

    print("BOOTSTRAP_PACKET_BEGIN")
    print(f"user-session: {packet['user_session']}")
    print(f"current-working-repo: {packet['current_working_repo']}")
    print(f"current-working-repo-path: {packet['current_working_repo_path']}")
    print(f"target-repo: {packet['target_repo']} ({packet['target_repo_status']})")
    print(f"purpose: {packet['purpose']}")
    print(f"constraints: {packet['constraints']}")
    print(f"ui-impact: {packet['ui_impact']}")
    print(f"expected-result: {packet['expected_result']}")
    print(f"template-id: {packet['template_id']}")
    print(f"template-version: {packet['template_version']}")
    print(f"deploy-profile: {packet['deploy_profile']}")
    print(f"override-scope: {packet['override_scope']}")
    print(f"lifecycle-action: {packet['lifecycle_action']}")
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

    print("TARGET_REPO_SEED_FILES_BEGIN")
    for item in packet["target_repo_seed_files"]:
        print(f"- source-template: {item['source_template']}")
        print(f"  destination: {item['destination']}")
        print(f"  role: {item['role']}")
        print(f"  purpose: {item['purpose']}")
        print("  required-placeholders:")
        for placeholder in item["required_placeholders"]:
            print(f"  - {placeholder}")
    print("TARGET_REPO_SEED_FILES_END")
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
    workspace_check = build_workspace_check(
        cwd,
        current_repo_maintenance=args.current_repo_maintenance,
    )

    if args.workspace_check:
        if args.json:
            print(json.dumps({"workspace_check": workspace_check}, ensure_ascii=False, indent=2))
        else:
            print_workspace_check(workspace_check)
        return 0 if workspace_check["startup_ready"] else 3

    required_template_flags = {
        "template_id": args.template_id,
        "template_version": args.template_version,
        "deploy_profile": args.deploy_profile,
        "override_scope": args.override_scope,
        "lifecycle_action": args.lifecycle_action,
    }
    missing_template_flags = [name for name, value in required_template_flags.items() if not value]
    if missing_template_flags:
        missing_rendered = ", ".join(f"--{item.replace('_', '-')}" for item in missing_template_flags)
        raise SystemExit(f"Missing required arguments: {missing_rendered}")

    if not workspace_check["control_plane_complete"]:
        raise FileNotFoundError(workspace_check["message"])

    clever_root = Path(workspace_check["clever_root"])
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
        template_id=args.template_id,
        template_version=args.template_version,
        deploy_profile=args.deploy_profile,
        override_scope=args.override_scope,
        lifecycle_action=args.lifecycle_action,
        recorded_template_id=args.recorded_template_id,
        recorded_template_version=args.recorded_template_version,
        recorded_deploy_profile=args.recorded_deploy_profile,
        ssot_docs_read=build_ssot_docs(
            clever_root,
            preferred_branch=branch_name,
            preferred_checkout_name=git_root.name,
        ),
        issue_repo=repo_full_name(change_repo_path) or CHANGE_REPO_NAME,
        workspace_check=workspace_check,
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
