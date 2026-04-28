#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import re
import shutil
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
DEFAULT_GITHUB_OWNER = "EVNSolution"
DEFAULT_EXPECTED_GITHUB_LOGIN: str | None = None
GITHUB_LOGIN_REQUEST_MESSAGE = (
    "Ask the user for their GitHub login or profile URL only when the "
    "authenticated account cannot be inferred from gh CLI or must be overridden, "
    "then set CLEVER_EXPECTED_GITHUB_LOGIN or pass --expected-github-login."
)

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
    {
        "source_template": "clever-agent-project/docs/templates/apply-target-repo-rulesets.sh",
        "destination": "scripts/apply-github-rulesets.sh",
        "role": "GitHub repository ruleset bootstrap",
        "purpose": (
            "Apply the standard target repo branch rulesets: protect main, "
            "require PR-only updates for dev, and leave other branches unrestricted. "
            "The target repo must be public when the organization uses GitHub Free."
        ),
        "required_placeholders": [
            "target_repo_full_name",
        ],
    },
    {
        "source_template": "clever-agent-project/docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md",
        "destination": ".github/PULL_REQUEST_TEMPLATE.md",
        "role": "PR review context/wiki completion checklist",
        "purpose": (
            "Require dev and main PR review work to finish with service, context, "
            "or wiki updates, or a documented not-needed decision."
        ),
        "required_placeholders": [
            "target_repo",
            "target_service",
        ],
    },
]


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def run_command_result(cmd: list[str], cwd: Path | None = None) -> CommandResult:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        return CommandResult(127, "", str(exc))
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def run_command(cmd: list[str], cwd: Path | None = None) -> str | None:
    result = run_command_result(cmd, cwd=cwd)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


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


def add_preflight_check(
    checks: list[dict[str, Any]],
    *,
    name: str,
    passed: bool,
    message: str,
    details: dict[str, Any] | None = None,
) -> None:
    check: dict[str, Any] = {
        "name": name,
        "status": "pass" if passed else "fail",
        "message": message,
    }
    if details:
        check["details"] = details
    checks.append(check)


def command_message(result: CommandResult) -> str:
    output = (result.stderr or result.stdout).strip()
    return output if output else f"command exited with {result.returncode}"


def parse_json_object(raw: str) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def normalize_repo_full_name(repo: str | None, *, github_owner: str) -> str | None:
    if not repo:
        return None
    return repo if "/" in repo else f"{github_owner}/{repo}"


def normalize_github_login_identifier(value: str | None) -> str | None:
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return None

    candidate = re.split(r"[?#]", candidate, maxsplit=1)[0].strip().rstrip("/")
    if candidate.startswith("@"):
        candidate = candidate[1:]

    github_url_match = re.match(
        r"^(?:https?://)?(?:www\.)?github\.com/(?P<login>[^/]+)(?:/.*)?$",
        candidate,
        flags=re.IGNORECASE,
    )
    if github_url_match:
        candidate = github_url_match.group("login")

    ssh_url_match = re.match(
        r"^git@github\.com:(?P<login>[^/]+)/?.*$",
        candidate,
        flags=re.IGNORECASE,
    )
    if ssh_url_match:
        candidate = ssh_url_match.group("login")

    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    if candidate.startswith("@"):
        candidate = candidate[1:]

    return candidate or None


def collect_control_plane_paths(workspace_check: dict[str, Any]) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    repos = workspace_check.get("repos", {})
    for repo_name_value in CONTROL_PLANE_REPOS:
        repo_state = repos.get(repo_name_value, {})
        checkout_path = repo_state.get("checkout_path")
        if checkout_path:
            paths[repo_name_value] = Path(checkout_path)
    return paths


def check_by_name(checks: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    return next((check for check in checks if check.get("name") == name), None)


def build_preflight_auto_skipped_questions(
    *,
    checks: list[dict[str, Any]],
    workspace_check: dict[str, Any],
    normalized_expected_github_login: str | None,
    github_login: str | None,
) -> list[dict[str, str]]:
    skipped: list[dict[str, str]] = []

    if normalized_expected_github_login is None and github_login:
        skipped.append(
            {
                "question": "github_login",
                "reason": "gh CLI inferred the authenticated GitHub account.",
                "evidence": github_login,
            }
        )

    agent_action = workspace_check.get("agent_action")
    if agent_action:
        skipped.append(
            {
                "question": "startup_location",
                "reason": "workspace_check.agent_action already selected the startup path.",
                "evidence": str(agent_action),
            }
        )

    clean_check = check_by_name(checks, "control-plane-worktrees-clean")
    if clean_check:
        skipped.append(
            {
                "question": "dirty_state",
                "reason": "control-plane worktree cleanliness was checked automatically.",
                "evidence": str(clean_check["status"]),
            }
        )

    return skipped


def build_preflight_recovery_actions(
    *,
    checks: list[dict[str, Any]],
    workspace_check: dict[str, Any],
    github_owner: str,
) -> list[dict[str, str]]:
    failed = {check["name"]: check for check in checks if check.get("status") != "pass"}
    actions: list[dict[str, str]] = []

    def add(check: str, action: str, command: str | None = None) -> None:
        item = {"check": check, "action": action}
        if command:
            item["command"] = command
        actions.append(item)

    if "gh-cli" in failed:
        add(
            "gh-cli",
            "Install GitHub CLI, then authenticate before rerunning preflight.",
            "gh auth login",
        )
    if "gh-auth" in failed:
        add(
            "gh-auth",
            "Authenticate GitHub CLI for the current user.",
            "gh auth login && gh auth setup-git",
        )
    if "github-account" in failed:
        add(
            "github-account",
            "Run gh auth login or provide the GitHub login/profile URL to use as an override.",
            "gh auth login",
        )
    if "github-org-membership" in failed:
        add(
            "github-org-membership",
            f"Use a GitHub account with active {github_owner} org membership or request access.",
        )
    if "workspace" in failed:
        missing = workspace_check.get("missing_repositories") or []
        if missing:
            add(
                "workspace",
                "Clone the missing control-plane repositories into the same workspace root.",
                "\n".join(
                    f"git clone https://github.com/{github_owner}/{repo_name_value}.git"
                    for repo_name_value in missing
                ),
            )
        else:
            add(
                "workspace",
                "Move to the recommended CLEVER workspace or rerun from clever-agent-project.",
            )
    if "control-plane-remotes" in failed:
        add(
            "control-plane-remotes",
            f"Fix control-plane origin remotes so they point to {github_owner}/*.",
        )
    if "control-plane-worktrees-clean" in failed:
        add(
            "control-plane-worktrees-clean",
            "Review, commit, stash, or discard dirty control-plane worktree changes before startup.",
            "git status --short",
        )
    if "control-plane-remote-fetch" in failed:
        add(
            "control-plane-remote-fetch",
            "Check network and remote permissions, then verify each control-plane origin can fetch.",
            "git fetch --dry-run origin",
        )
    if "github-repo-access" in failed:
        add(
            "github-repo-access",
            "Confirm the authenticated GitHub account can read all public control-plane repositories.",
            f"gh repo view {github_owner}/{START_REPO_NAME}",
        )
    if "github-issue-pr-access" in failed:
        add(
            "github-issue-pr-access",
            "Confirm issue and PR list access for every control-plane repository.",
            f"gh issue list --repo {github_owner}/{CHANGE_REPO_NAME} --limit 1",
        )
    if "ruleset-read" in failed:
        add(
            "ruleset-read",
            "Confirm the token can read repository rulesets for the control-plane repositories.",
            f"gh api repos/{github_owner}/{START_REPO_NAME}/rulesets",
        )
    if "target-repo-admin" in failed:
        add(
            "target-repo-admin",
            "Use a public target repository where the authenticated account has ADMIN permission.",
        )

    return actions


def build_preflight_next_questions(
    *,
    ready: bool,
    checks: list[dict[str, Any]],
    workspace_check: dict[str, Any],
    github_login: str | None,
) -> list[dict[str, str]]:
    failed = {check["name"]: check for check in checks if check.get("status") != "pass"}
    questions: list[dict[str, str]] = []

    if not ready:
        if "github-account" in failed and github_login is None:
            questions.append(
                {
                    "id": "github_login",
                    "prompt": "GitHub login 또는 profile URL을 알려 주세요.",
                    "reason": "gh CLI could not infer the authenticated account.",
                }
            )
        elif "github-account" in failed:
            questions.append(
                {
                    "id": "github_login_override",
                    "prompt": "현재 gh CLI 계정과 다른 GitHub login/profile URL을 써야 하나요?",
                    "reason": "The inferred GitHub account did not match the expected override.",
                }
            )

        if "control-plane-worktrees-clean" in failed:
            questions.append(
                {
                    "id": "dirty_worktree_resolution",
                    "prompt": "감지된 dirty 변경을 커밋, stash, 폐기, 또는 별도 PR 중 어떻게 처리할까요?",
                    "reason": "preflight found dirty control-plane worktrees.",
                }
            )

        return questions

    agent_action = workspace_check.get("agent_action")
    if agent_action == "proceed-with-hard-gate":
        questions.append(
            {
                "id": "startup_branch_input",
                "prompt": "작업 시작: 먼저 하려는 일을 한 줄로 적어 주세요.",
                "reason": "preflight passed and the workspace is ready for the startup template.",
            }
        )
    elif agent_action == "current-repo-maintenance":
        questions.append(
            {
                "id": "maintenance_target",
                "prompt": "현재 control-plane repo에서 고칠 대상과 기대 결과를 한 줄로 알려 주세요.",
                "reason": "preflight classified this session as repo-local maintenance.",
            }
        )

    return questions


def build_preflight_check(
    *,
    cwd: Path,
    expected_github_login: str | None = DEFAULT_EXPECTED_GITHUB_LOGIN,
    github_owner: str = DEFAULT_GITHUB_OWNER,
    admin: bool = False,
    target_repo_full_name: str | None = None,
    current_repo_maintenance: bool = False,
) -> dict[str, Any]:
    mode = "admin" if admin else "basic"
    checks: list[dict[str, Any]] = []
    normalized_expected_github_login = normalize_github_login_identifier(expected_github_login)

    git_path = shutil.which("git")
    add_preflight_check(
        checks,
        name="git-cli",
        passed=bool(git_path),
        message=git_path or "git CLI is required before CLEVER startup.",
    )

    gh_path = shutil.which("gh")
    add_preflight_check(
        checks,
        name="gh-cli",
        passed=bool(gh_path),
        message=gh_path or "GitHub CLI is required. Run `gh auth login` after installing gh.",
    )

    gh_auth_ok = False
    github_login: str | None = None
    if gh_path:
        auth_result = run_command_result(["gh", "auth", "status"])
        gh_auth_ok = auth_result.returncode == 0
        add_preflight_check(
            checks,
            name="gh-auth",
            passed=gh_auth_ok,
            message=(
                "`gh auth status` passed."
                if gh_auth_ok
                else f"`gh auth status` failed: {command_message(auth_result)}"
            ),
        )

        user_result = run_command_result(["gh", "api", "user", "--jq", ".login"])
        github_login = user_result.stdout.strip() if user_result.returncode == 0 else None
        if normalized_expected_github_login is None and github_login:
            login_ok = True
            account_message = f"GitHub account inferred from gh CLI: {github_login}."
        elif normalized_expected_github_login is None:
            login_ok = False
            account_message = (
                "Cannot infer GitHub account from gh CLI. "
                f"{GITHUB_LOGIN_REQUEST_MESSAGE}"
            )
        else:
            login_ok = (
                github_login is not None
                and github_login.lower() == normalized_expected_github_login.lower()
            )
            account_message = (
                f"GitHub account is {github_login}."
                if login_ok
                else (
                    "Expected GitHub account "
                    f"{normalized_expected_github_login}, got {github_login or command_message(user_result)}."
                )
            )
        add_preflight_check(
            checks,
            name="github-account",
            passed=login_ok,
            message=account_message,
            details={
                "expected": normalized_expected_github_login,
                "actual": github_login,
            },
        )
        membership_result = run_command_result(
            ["gh", "api", f"user/memberships/orgs/{github_owner}"]
        )
        membership_info = parse_json_object(membership_result.stdout)
        membership_ok = (
            membership_result.returncode == 0
            and membership_info is not None
            and membership_info.get("state") == "active"
        )
        add_preflight_check(
            checks,
            name="github-org-membership",
            passed=membership_ok,
            message=(
                f"GitHub account is an active member of {github_owner}."
                if membership_ok
                else (
                    f"Cannot confirm active {github_owner} org membership: "
                    f"{command_message(membership_result)}"
                )
            ),
            details={
                "org": github_owner,
                "state": membership_info.get("state") if membership_info else None,
                "role": membership_info.get("role") if membership_info else None,
            },
        )
    else:
        add_preflight_check(
            checks,
            name="gh-auth",
            passed=False,
            message="Cannot run `gh auth status` because gh CLI is missing.",
        )
        add_preflight_check(
            checks,
            name="github-account",
            passed=False,
            message=(
                f"Cannot confirm expected GitHub account {normalized_expected_github_login}."
                if normalized_expected_github_login
                else f"Cannot confirm GitHub account because gh CLI is missing. {GITHUB_LOGIN_REQUEST_MESSAGE}"
            ),
            details={"expected": normalized_expected_github_login, "actual": None},
        )
        add_preflight_check(
            checks,
            name="github-org-membership",
            passed=False,
            message=f"Cannot confirm {github_owner} org membership because gh CLI is missing.",
            details={"org": github_owner, "state": None, "role": None},
        )

    workspace_check = build_workspace_check(
        cwd,
        current_repo_maintenance=current_repo_maintenance,
    )
    workspace_ok = bool(workspace_check.get("startup_ready"))
    add_preflight_check(
        checks,
        name="workspace",
        passed=workspace_ok,
        message=workspace_check.get("message", "workspace check completed"),
        details={
            "agent_action": workspace_check.get("agent_action"),
            "control_plane_complete": workspace_check.get("control_plane_complete"),
        },
    )

    control_paths = collect_control_plane_paths(workspace_check)

    remote_messages: list[str] = []
    remote_ok = len(control_paths) == len(CONTROL_PLANE_REPOS)
    for repo_name_value in CONTROL_PLANE_REPOS:
        repo_path = control_paths.get(repo_name_value)
        expected_full_name = f"{github_owner}/{repo_name_value}"
        actual_full_name = repo_full_name(repo_path) if repo_path else None
        if actual_full_name != expected_full_name:
            remote_ok = False
            remote_messages.append(
                f"{repo_name_value}: expected {expected_full_name}, got {actual_full_name or 'missing'}"
            )
    add_preflight_check(
        checks,
        name="control-plane-remotes",
        passed=remote_ok,
        message=(
            f"All control-plane remotes point to {github_owner}."
            if remote_ok
            else "; ".join(remote_messages)
        ),
    )

    clean_messages: list[str] = []
    clean_ok = len(control_paths) == len(CONTROL_PLANE_REPOS)
    for repo_name_value, repo_path in control_paths.items():
        result = run_command_result(["git", "-C", str(repo_path), "status", "--short"])
        if result.returncode != 0 or result.stdout.strip():
            clean_ok = False
            clean_messages.append(
                f"{repo_name_value}: {command_message(result) if result.returncode != 0 else result.stdout.strip()}"
            )
    add_preflight_check(
        checks,
        name="control-plane-worktrees-clean",
        passed=clean_ok,
        message=(
            "All control-plane worktrees are clean."
            if clean_ok
            else "; ".join(clean_messages or ["control-plane checkout is incomplete"])
        ),
    )

    fetch_messages: list[str] = []
    fetch_ok = len(control_paths) == len(CONTROL_PLANE_REPOS)
    for repo_name_value, repo_path in control_paths.items():
        result = run_command_result(["git", "-C", str(repo_path), "fetch", "--dry-run", "origin"])
        if result.returncode != 0:
            fetch_ok = False
            fetch_messages.append(f"{repo_name_value}: {command_message(result)}")
    add_preflight_check(
        checks,
        name="control-plane-remote-fetch",
        passed=fetch_ok,
        message=(
            "All control-plane remotes are reachable."
            if fetch_ok
            else "; ".join(fetch_messages or ["control-plane checkout is incomplete"])
        ),
    )

    repo_access_messages: list[str] = []
    issue_pr_messages: list[str] = []
    ruleset_messages: list[str] = []
    repo_access_ok = bool(gh_path) and len(control_paths) == len(CONTROL_PLANE_REPOS)
    issue_pr_ok = bool(gh_path) and len(control_paths) == len(CONTROL_PLANE_REPOS)
    ruleset_ok = bool(gh_path) and len(control_paths) == len(CONTROL_PLANE_REPOS)
    for repo_name_value in CONTROL_PLANE_REPOS:
        expected_full_name = f"{github_owner}/{repo_name_value}"
        view_result = run_command_result(
            [
                "gh",
                "repo",
                "view",
                expected_full_name,
                "--json",
                "nameWithOwner,visibility,isPrivate,viewerPermission",
            ]
        )
        repo_info = parse_json_object(view_result.stdout)
        if view_result.returncode != 0 or not repo_info:
            repo_access_ok = False
            repo_access_messages.append(f"{expected_full_name}: {command_message(view_result)}")
        elif repo_info.get("visibility") != "PUBLIC" or repo_info.get("isPrivate"):
            repo_access_ok = False
            repo_access_messages.append(f"{expected_full_name}: repository must be PUBLIC")

        for issue_or_pr in ("issue", "pr"):
            list_result = run_command_result(
                [
                    "gh",
                    issue_or_pr,
                    "list",
                    "--repo",
                    expected_full_name,
                    "--limit",
                    "1",
                    "--json",
                    "number",
                ]
            )
            if list_result.returncode != 0:
                issue_pr_ok = False
                issue_pr_messages.append(f"{expected_full_name} {issue_or_pr}: {command_message(list_result)}")

        ruleset_result = run_command_result(["gh", "api", f"repos/{expected_full_name}/rulesets"])
        if ruleset_result.returncode != 0:
            ruleset_ok = False
            ruleset_messages.append(f"{expected_full_name}: {command_message(ruleset_result)}")

    add_preflight_check(
        checks,
        name="github-repo-access",
        passed=repo_access_ok,
        message=(
            "All control-plane GitHub repos are readable and public."
            if repo_access_ok
            else "; ".join(repo_access_messages or ["gh CLI is unavailable or workspace is incomplete"])
        ),
    )
    add_preflight_check(
        checks,
        name="github-issue-pr-access",
        passed=issue_pr_ok,
        message=(
            "Issues and PRs are readable for every control-plane repo."
            if issue_pr_ok
            else "; ".join(issue_pr_messages or ["gh CLI is unavailable or workspace is incomplete"])
        ),
    )
    add_preflight_check(
        checks,
        name="ruleset-read",
        passed=ruleset_ok,
        message=(
            "Rulesets are readable for every control-plane repo."
            if ruleset_ok
            else "; ".join(ruleset_messages or ["gh CLI is unavailable or workspace is incomplete"])
        ),
    )

    normalized_target_repo = normalize_repo_full_name(
        target_repo_full_name,
        github_owner=github_owner,
    )
    if admin:
        target_admin_ok = False
        target_admin_message = "--admin-preflight requires --target-repo or --target-repo-full-name."
        if normalized_target_repo:
            view_result = run_command_result(
                [
                    "gh",
                    "repo",
                    "view",
                    normalized_target_repo,
                    "--json",
                    "nameWithOwner,visibility,isPrivate,viewerPermission",
                ]
            )
            repo_info = parse_json_object(view_result.stdout)
            if view_result.returncode != 0 or not repo_info:
                target_admin_message = (
                    f"{normalized_target_repo}: cannot confirm admin permission: "
                    f"{command_message(view_result)}"
                )
            else:
                permission = repo_info.get("viewerPermission")
                is_public = repo_info.get("visibility") == "PUBLIC" and not repo_info.get("isPrivate")
                target_admin_ok = permission == "ADMIN" and is_public
                target_admin_message = (
                    f"{normalized_target_repo}: ADMIN permission and PUBLIC visibility confirmed."
                    if target_admin_ok
                    else (
                        f"{normalized_target_repo}: expected PUBLIC repo with ADMIN permission, "
                        f"got visibility={repo_info.get('visibility')} permission={permission}."
                    )
                )
        add_preflight_check(
            checks,
            name="target-repo-admin",
            passed=target_admin_ok,
            message=target_admin_message,
            details={"target_repo": normalized_target_repo},
        )

    ready = all(check["status"] == "pass" for check in checks)
    auto_skipped_questions = build_preflight_auto_skipped_questions(
        checks=checks,
        workspace_check=workspace_check,
        normalized_expected_github_login=normalized_expected_github_login,
        github_login=github_login,
    )
    recovery_actions = build_preflight_recovery_actions(
        checks=checks,
        workspace_check=workspace_check,
        github_owner=github_owner,
    )
    next_questions = build_preflight_next_questions(
        ready=ready,
        checks=checks,
        workspace_check=workspace_check,
        github_login=github_login,
    )
    return {
        "mode": mode,
        "ready": ready,
        "expected_github_login": normalized_expected_github_login,
        "github_login": github_login,
        "github_owner": github_owner,
        "target_repo": normalized_target_repo,
        "workspace_check": workspace_check,
        "checks": checks,
        "auto_skipped_questions": auto_skipped_questions,
        "recovery_actions": recovery_actions,
        "next_questions": next_questions,
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
            "After the project-start issue is approved and created, propose public target "
            "repo creation or confirmation before cloning locally."
            if requires_new_repo
            else "After the project-start issue is approved and created, confirm the current "
            "repo is the target execution repo and refresh the local checkout."
        )
    )
    target_repo_visibility = "public-when-created"
    visibility_reason = (
        "GitHub Free organization rulesets are enforced on public repositories. "
        "Private repository ruleset enforcement requires GitHub Team, GitHub Pro, "
        "or GitHub Enterprise Cloud."
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
            "target_repo_visibility": target_repo_visibility,
            "visibility_reason": visibility_reason,
            "status": "proposed-after-approval",
            "proposal": repo_bootstrap_proposal,
            "post_create_clone": [
                "create-or-confirm public target repo after project-start approval",
                "clone-or-pull the target repo locally",
                "copy target repo seed files before handoff",
                "apply GitHub rulesets after dev exists",
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
        "--preflight",
        action="store_true",
        help="Run the strict startup preflight gate before project-start work.",
    )
    parser.add_argument(
        "--admin-preflight",
        action="store_true",
        help="Run startup preflight plus target repo admin checks before repo/ruleset changes.",
    )
    parser.add_argument(
        "--expected-github-login",
        default=os.environ.get("CLEVER_EXPECTED_GITHUB_LOGIN") or DEFAULT_EXPECTED_GITHUB_LOGIN,
        help=(
            "Expected GitHub login or profile URL for gh authenticated operations. "
            "No shared default is assumed; ask the user on first startup."
        ),
    )
    parser.add_argument(
        "--github-owner",
        default=os.environ.get("CLEVER_GITHUB_OWNER", DEFAULT_GITHUB_OWNER),
        help="GitHub owner or organization expected for CLEVER repositories.",
    )
    parser.add_argument(
        "--target-repo-full-name",
        help="Target repo full name for admin preflight, for example EVNSolution/example.",
    )
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


def print_preflight_check(preflight_check: dict[str, Any]) -> None:
    print("PREFLIGHT_CHECK_BEGIN")
    print(f"mode: {preflight_check['mode']}")
    print(f"ready: {'yes' if preflight_check['ready'] else 'no'}")
    print(f"github-owner: {preflight_check['github_owner']}")
    print(
        "expected-github-login: "
        f"{preflight_check['expected_github_login'] or 'needs-user-input'}"
    )
    print(f"github-login: {preflight_check['github_login'] or 'unknown'}")
    if preflight_check.get("target_repo"):
        print(f"target-repo: {preflight_check['target_repo']}")
    print("checks:")
    for check in preflight_check["checks"]:
        print(f"- {check['name']}: {check['status']} - {check['message']}")
    if preflight_check.get("auto_skipped_questions"):
        print("auto-skipped-questions:")
        for item in preflight_check["auto_skipped_questions"]:
            print(
                f"- {item['question']}: {item['reason']} "
                f"(evidence: {item['evidence']})"
            )
    if preflight_check.get("recovery_actions"):
        print("recovery-actions:")
        for item in preflight_check["recovery_actions"]:
            print(f"- {item['check']}: {item['action']}")
            if item.get("command"):
                print(f"  command: {item['command']}")
    if preflight_check.get("next_questions"):
        print("next-questions:")
        for item in preflight_check["next_questions"]:
            print(f"- {item['id']}: {item['prompt']} ({item['reason']})")
    print("PREFLIGHT_CHECK_END")


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

    if args.preflight or args.admin_preflight:
        target_repo_for_admin = args.target_repo_full_name or args.target_repo
        preflight_check = build_preflight_check(
            cwd=cwd,
            expected_github_login=args.expected_github_login,
            github_owner=args.github_owner,
            admin=args.admin_preflight,
            target_repo_full_name=target_repo_for_admin,
            current_repo_maintenance=args.current_repo_maintenance,
        )
        if args.json:
            print(json.dumps({"preflight_check": preflight_check}, ensure_ascii=False, indent=2))
        else:
            print_preflight_check(preflight_check)
        return 0 if preflight_check["ready"] else 3

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
