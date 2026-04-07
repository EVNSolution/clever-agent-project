from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / ".codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py"
)
WORKTREES_ROOT = Path(
    os.environ.get(
        "SUPERPOWERS_WORKTREES_ROOT",
        str(Path.home() / ".config/superpowers/worktrees"),
    )
)
CHANGE_WORKTREE = WORKTREES_ROOT / "clever-change-control/project-start-model"
CONTEXT_WORKTREE = WORKTREES_ROOT / "clever-context-monorepo/project-start-model"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap_clever_work", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_packet(**overrides):
    module = load_module()
    return module.build_packet(
        user_session="agent-session",
        current_working_repo="clever-agent-project",
        current_working_repo_path=str(REPO_ROOT),
        target_repo=overrides.get("target_repo", "clever-analytics-api"),
        target_repo_status=overrides.get("target_repo_status", "provided"),
        purpose="Launch a new analytics workflow",
        constraints="Use the approved project-start intake",
        ui_impact="unknown",
        expected_result="A ready-to-approve project-start issue draft",
        ssot_docs_read=[
            "/workspace/clever-context-monorepo/README.md",
            "/workspace/clever-change-control/README.md",
        ],
    )


def run_cli(*args):
    proc = subprocess.run(
        ["python3", str(MODULE_PATH), "--cwd", str(REPO_ROOT), "--json", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def test_build_packet_uses_project_start_fields():
    packet = build_packet()

    assert "project_start_issue" in packet
    assert "change_id" not in packet
    assert "target_service" not in packet
    assert "service_doc_draft" not in packet
    assert "service_doc_path" not in packet

    draft = packet["project_start_issue"]
    assert draft["title"] == "Launch a new analytics workflow"
    assert draft["status"] == "draft"
    assert draft["canonical_reference"] == "pending-project-start-issue"
    assert draft["body"].startswith("## Purpose")
    assert "## Requested Flow" not in draft["body"]
    assert (
        "- target repo proposal: proposed target repo: clever-analytics-api"
        in draft["body"]
    )
    assert (
        "- target service proposal: deferred until repo bootstrap; target service is optional "
        "at project-start and should only be confirmed if it becomes necessary."
        in draft["body"]
    )
    for section in [
        "## Target Repo Proposal",
        "## Target Service Proposal",
        "## Repo Bootstrap Proposal",
        "## Canonical Linkage Expectations",
        "## Repo Session Handoff",
    ]:
        assert section in draft["body"]


@pytest.mark.skipif(
    not CHANGE_WORKTREE.is_dir() or not CONTEXT_WORKTREE.is_dir(),
    reason="worktree regression requires CLEVER worktree fixtures",
)
def test_cli_from_worktree_resolves_real_repo_identity_and_ssot_checkouts():
    proc = subprocess.run(
        ["python3", str(MODULE_PATH), "--cwd", str(CHANGE_WORKTREE), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    packet = json.loads(proc.stdout)

    assert packet["current_working_repo"] == "clever-change-control"
    assert packet["current_working_repo_path"] == str(CHANGE_WORKTREE)
    assert str(CONTEXT_WORKTREE / "README.md") in packet["ssot_docs_read"]
    assert (
        str(CHANGE_WORKTREE / ".github/ISSUE_TEMPLATE/project-start.yml")
        in packet["ssot_docs_read"]
    )


@pytest.mark.skipif(
    not CHANGE_WORKTREE.is_dir() or not CONTEXT_WORKTREE.is_dir(),
    reason="worktree regression requires CLEVER worktree fixtures",
)
def test_cli_from_start_repo_prefers_matching_ssot_worktrees_for_current_branch():
    packet = run_cli()

    assert str(CONTEXT_WORKTREE / "README.md") in packet["ssot_docs_read"]
    assert (
        str(CHANGE_WORKTREE / ".github/ISSUE_TEMPLATE/project-start.yml")
        in packet["ssot_docs_read"]
    )
    assert str(REPO_ROOT.parent / "clever-context-monorepo/README.md") not in packet["ssot_docs_read"]


def test_build_packet_distinguishes_start_repo_from_target_repo_bootstrap():
    packet = build_packet(target_repo="clever-analytics-api")

    assert packet["current_working_repo"] == "clever-agent-project"
    assert packet["target_repo"] == "clever-analytics-api"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever-agent-project"
    assert repo_bootstrap["target_repo"] == "clever-analytics-api"
    assert repo_bootstrap["requires_new_repo"] is True
    assert repo_bootstrap["status"] == "proposed-after-approval"


def test_build_packet_includes_post_create_clone_and_handoff_plan():
    packet = build_packet()

    repo_bootstrap = packet["repo_bootstrap"]
    handoff = packet["repo_session_handoff"]

    assert repo_bootstrap["post_create_clone"] == [
        "create-or-confirm target repo after project-start approval",
        "clone-or-pull the target repo locally",
        "verify local checkout is ready for follow-on work",
    ]
    assert handoff["recommended_session"] == "new-target-repo-session"
    assert handoff["status"] == "recommended-after-clone"
    assert "Switch to the cloned target repo" in handoff["summary"]


def test_build_ssot_docs_uses_project_start_aligned_surface():
    module = load_module()
    clever_root = module.find_clever_root(REPO_ROOT)

    docs = module.build_ssot_docs(clever_root)

    assert str(clever_root / "clever-context-monorepo/docs/wiki/index.md") in docs
    assert (
        str(clever_root / "clever-change-control/.github/ISSUE_TEMPLATE/project-start.yml")
        in docs
    )
    assert str(clever_root / "clever-change-control/changes") in docs
    assert str(clever_root / "clever-change-control/releases") in docs
    assert str(clever_root / "clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml") not in docs
    assert str(clever_root / "clever-context-monorepo/docs/services/service-template.md") not in docs


def test_cli_without_target_repo_keeps_target_repo_as_needs_confirmation():
    packet = run_cli()

    assert packet["current_working_repo"] == "clever-agent-project"
    assert packet["target_repo"] == "needs-confirmation"
    assert packet["target_repo_status"] == "needs-confirmation"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever-agent-project"
    assert repo_bootstrap["target_repo"] == "needs-confirmation"
    assert repo_bootstrap["requires_new_repo"] is None
    assert repo_bootstrap["target_repo_status"] == "needs-confirmation"
    assert "confirm the target repo" in repo_bootstrap["proposal"]
    assert (
        "- target repo proposal: deferred until approval; confirm which GitHub repo should be "
        "created or selected after the project-start issue exists."
        in packet["project_start_issue"]["body"]
    )


def test_resolve_repo_checkout_prefers_matching_branch_in_wrapper_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = load_module()
    clever_root = tmp_path
    wrapper = clever_root / "clever-change-control"
    wrapper.mkdir()
    branch_a = wrapper / "feature-a"
    branch_b = wrapper / "feature-b"
    branch_a.mkdir()
    branch_b.mkdir()

    monkeypatch.setattr(module, "list_git_worktrees", lambda _path: [])
    monkeypatch.setattr(module, "is_checkout_root", lambda path: path in {branch_a, branch_b})
    monkeypatch.setattr(module, "repo_name", lambda _path: "clever-change-control")
    monkeypatch.setattr(module, "current_branch", lambda path: path.name)

    resolved = module.resolve_repo_checkout(
        clever_root=clever_root,
        repo_name_value="clever-change-control",
        preferred_branch="feature-b",
    )

    assert resolved == branch_b.resolve()


def test_cli_with_current_repo_target_marks_requires_new_repo_false():
    packet = run_cli("--target-repo", "clever-agent-project")

    assert packet["current_working_repo"] == "clever-agent-project"
    assert packet["target_repo"] == "clever-agent-project"
    assert packet["target_repo_status"] == "provided"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever-agent-project"
    assert repo_bootstrap["target_repo"] == "clever-agent-project"
    assert repo_bootstrap["target_repo_status"] == "provided"
    assert repo_bootstrap["requires_new_repo"] is False
    assert (
        "- target repo proposal: confirm the current working repo (clever-agent-project) as "
        "the execution repo"
        in packet["project_start_issue"]["body"]
    )


def test_resolve_repo_checkout_prefers_matching_branch_with_real_git_worktrees(tmp_path: Path):
    module = load_module()
    sources_root = tmp_path / "sources"
    clever_root = tmp_path / "wrapper-root"
    main_repo = sources_root / "clever-change-control"
    wrapper = clever_root / "clever-change-control"

    main_repo.mkdir(parents=True)
    wrapper.mkdir(parents=True)

    subprocess.run(["git", "init", str(main_repo)], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(main_repo), "config", "user.name", "Test User"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(main_repo), "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    (main_repo / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(main_repo), "add", "README.md"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(main_repo), "commit", "-m", "seed"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(main_repo),
            "worktree",
            "add",
            "-b",
            "feature-a",
            str(wrapper / "feature-a"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(main_repo),
            "worktree",
            "add",
            "-b",
            "feature-b",
            str(wrapper / "feature-b"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    resolved = module.resolve_repo_checkout(
        clever_root=clever_root,
        repo_name_value="clever-change-control",
        preferred_branch="feature-b",
    )

    assert resolved == (wrapper / "feature-b").resolve()
