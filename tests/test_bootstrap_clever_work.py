from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / ".codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py"
)
WORKTREES_ROOT = Path("/Users/jiin/.config/superpowers/worktrees")
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
        current_working_repo="clever_agent_project",
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


def test_build_packet_distinguishes_start_repo_from_target_repo_bootstrap():
    packet = build_packet(target_repo="clever-analytics-api")

    assert packet["current_working_repo"] == "clever_agent_project"
    assert packet["target_repo"] == "clever-analytics-api"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever_agent_project"
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

    assert packet["current_working_repo"] == "clever_agent_project"
    assert packet["target_repo"] == "needs-confirmation"
    assert packet["target_repo_status"] == "needs-confirmation"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever_agent_project"
    assert repo_bootstrap["target_repo"] == "needs-confirmation"
    assert repo_bootstrap["requires_new_repo"] is None
    assert repo_bootstrap["target_repo_status"] == "needs-confirmation"
    assert "confirm the target repo" in repo_bootstrap["proposal"]


def test_cli_with_current_repo_target_marks_requires_new_repo_false():
    packet = run_cli("--target-repo", "clever_agent_project")

    assert packet["current_working_repo"] == "clever_agent_project"
    assert packet["target_repo"] == "clever_agent_project"
    assert packet["target_repo_status"] == "provided"

    repo_bootstrap = packet["repo_bootstrap"]
    assert repo_bootstrap["source_repo"] == "clever_agent_project"
    assert repo_bootstrap["target_repo"] == "clever_agent_project"
    assert repo_bootstrap["target_repo_status"] == "provided"
    assert repo_bootstrap["requires_new_repo"] is False
