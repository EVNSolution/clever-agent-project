from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / ".codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py"
)


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
        purpose="Launch a new analytics workflow",
        constraints="Use the approved project-start intake",
        ui_impact="unknown",
        expected_result="A ready-to-approve project-start issue draft",
        ssot_docs_read=[
            "/workspace/clever-context-monorepo/README.md",
            "/workspace/clever-change-control/README.md",
        ],
    )


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
