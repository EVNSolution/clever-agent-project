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
    / ".agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py"
)
WORKTREES_ROOT = Path(
    os.environ.get(
        "SUPERPOWERS_WORKTREES_ROOT",
        str(Path.home() / ".config/superpowers/worktrees"),
    )
)
CHANGE_WORKTREE = WORKTREES_ROOT / "clever-change-control/project-start-model"
CONTEXT_WORKTREE = WORKTREES_ROOT / "clever-context-monorepo/project-start-model"


def git_current_branch(path: Path) -> str | None:
    if not path.is_dir():
        return None
    proc = subprocess.run(
        ["git", "-C", str(path), "branch", "--show-current"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    branch = proc.stdout.strip()
    return branch or None


CURRENT_BRANCH = git_current_branch(REPO_ROOT)
CHANGE_WORKTREE_BRANCH = git_current_branch(CHANGE_WORKTREE)
CONTEXT_WORKTREE_BRANCH = git_current_branch(CONTEXT_WORKTREE)


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
        ui_impact=overrides.get("ui_impact", "unknown"),
        expected_result="A ready-to-approve project-start issue draft",
        ssot_docs_read=[
            "/workspace/clever-context-monorepo/README.md",
            "/workspace/clever-change-control/README.md",
        ],
        template_id=overrides.get("template_id", "test-erik-project-template"),
        template_version=overrides.get("template_version", "v1"),
        deploy_profile=overrides.get("deploy_profile", "preview-dev-prod-monorepo"),
        override_scope=overrides.get("override_scope", "customer-config-only"),
        lifecycle_action=overrides.get("lifecycle_action", "adopt"),
        recorded_template_id=overrides.get("recorded_template_id"),
        recorded_template_version=overrides.get("recorded_template_version"),
        recorded_deploy_profile=overrides.get("recorded_deploy_profile"),
    )


def run_cli(*args):
    proc = subprocess.run(
        [
            "python3",
            str(MODULE_PATH),
            "--cwd",
            str(REPO_ROOT),
            "--json",
            "--template-id",
            "test-erik-project-template",
            "--template-version",
            "v1",
            "--deploy-profile",
            "preview-dev-prod-monorepo",
            "--override-scope",
            "customer-config-only",
            "--lifecycle-action",
            "adopt",
            *args,
        ],
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
        "## Template Harness",
        "## Repo Bootstrap Proposal",
        "## Canonical Linkage Expectations",
        "## Repo Session Handoff",
    ]:
        assert section in draft["body"]


def test_build_packet_includes_template_harness_metadata():
    packet = build_packet()

    assert packet["template_id"] == "test-erik-project-template"
    assert packet["template_version"] == "v1"
    assert packet["deploy_profile"] == "preview-dev-prod-monorepo"
    assert packet["override_scope"] == "customer-config-only"
    assert packet["lifecycle_action"] == "adopt"

    draft = packet["project_start_issue"]
    assert "## Template Harness" in draft["body"]
    assert "- template_id: test-erik-project-template" in draft["body"]
    assert "- template_version: v1" in draft["body"]
    assert "- deploy_profile: preview-dev-prod-monorepo" in draft["body"]
    assert "- override_scope: customer-config-only" in draft["body"]
    assert "- lifecycle_action: adopt" in draft["body"]


def test_build_packet_accepts_explicit_template_harness_metadata():
    packet = build_packet(
        template_id="test-erik-project-template",
        template_version="v1",
        deploy_profile="preview-dev-prod-monorepo",
        override_scope="customer-config-only",
        lifecycle_action="adopt",
    )

    assert packet["template_id"] == "test-erik-project-template"
    assert packet["template_version"] == "v1"
    assert packet["deploy_profile"] == "preview-dev-prod-monorepo"
    assert packet["override_scope"] == "customer-config-only"
    assert packet["lifecycle_action"] == "adopt"

    draft = packet["project_start_issue"]
    assert "- template_id: test-erik-project-template" in draft["body"]
    assert "- template_version: v1" in draft["body"]
    assert "- deploy_profile: preview-dev-prod-monorepo" in draft["body"]
    assert "- override_scope: customer-config-only" in draft["body"]
    assert "- lifecycle_action: adopt" in draft["body"]


def test_build_packet_rejects_invalid_lifecycle_action():
    with pytest.raises(ValueError, match="Unsupported lifecycle_action"):
        build_packet(lifecycle_action="archive")


def test_build_packet_rejects_invalid_template_id():
    with pytest.raises(ValueError, match="template_id must use lowercase"):
        build_packet(template_id="Bad Template")


def test_build_packet_rejects_invalid_ui_impact():
    with pytest.raises(ValueError, match="Unsupported ui_impact"):
        build_packet(ui_impact="maybe")


def test_build_packet_rejects_invalid_deploy_profile():
    with pytest.raises(ValueError, match="deploy_profile must use lowercase"):
        build_packet(deploy_profile="Preview/Profile")


def test_build_packet_requires_migrate_for_recorded_lineage_mismatch():
    with pytest.raises(ValueError, match="Use lifecycle_action=migrate"):
        build_packet(
            recorded_template_id="legacy-template",
            lifecycle_action="modify",
        )


def test_build_packet_allows_migrate_for_recorded_lineage_mismatch():
    packet = build_packet(
        recorded_template_id="legacy-template",
        lifecycle_action="migrate",
    )

    assert packet["lifecycle_action"] == "migrate"


@pytest.mark.skipif(
    not CHANGE_WORKTREE.is_dir()
    or not CONTEXT_WORKTREE.is_dir()
    or not CURRENT_BRANCH
    or CHANGE_WORKTREE_BRANCH != CURRENT_BRANCH
    or CONTEXT_WORKTREE_BRANCH != CURRENT_BRANCH,
    reason="worktree regression requires matching-branch CLEVER worktree fixtures",
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
    assert str(CHANGE_WORKTREE / "README.md") in packet["ssot_docs_read"]


@pytest.mark.skipif(
    not CHANGE_WORKTREE.is_dir()
    or not CONTEXT_WORKTREE.is_dir()
    or not CURRENT_BRANCH
    or CHANGE_WORKTREE_BRANCH != CURRENT_BRANCH
    or CONTEXT_WORKTREE_BRANCH != CURRENT_BRANCH,
    reason="worktree regression requires matching-branch CLEVER worktree fixtures",
)
def test_cli_from_start_repo_prefers_matching_ssot_worktrees_for_current_branch():
    packet = run_cli()

    assert str(CONTEXT_WORKTREE / "README.md") in packet["ssot_docs_read"]
    assert str(CHANGE_WORKTREE / "README.md") in packet["ssot_docs_read"]
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

    assert str(clever_root / "clever-change-control/changes") in docs
    assert str(clever_root / "clever-change-control/releases") in docs
    assert str(clever_root / "clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml") not in docs
    assert str(clever_root / "clever-context-monorepo/docs/wiki/index.md") not in docs
    assert str(clever_root / "clever-context-monorepo/docs/services/service-template.md") not in docs
    assert (
        str(clever_root / "clever-context-monorepo/docs/root/template-harness-governance.md")
        in docs
    )
    assert (
        str(clever_root / "clever-context-monorepo/docs/root/deploy-template-governance.md")
        in docs
    )
    assert str(clever_root / "clever-context-monorepo/docs/templates/index.md") in docs
    for path in docs:
        assert Path(path).exists(), f"Expected SSOT path to exist: {path}"


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


def test_cli_emits_template_harness_metadata_from_flags():
    packet = run_cli(
        "--template-id",
        "test-erik-project-template",
        "--template-version",
        "v1",
        "--deploy-profile",
        "preview-dev-prod-monorepo",
        "--override-scope",
        "customer-config-only",
        "--lifecycle-action",
        "adopt",
    )

    assert packet["template_id"] == "test-erik-project-template"
    assert packet["template_version"] == "v1"
    assert packet["deploy_profile"] == "preview-dev-prod-monorepo"
    assert packet["override_scope"] == "customer-config-only"
    assert packet["lifecycle_action"] == "adopt"
    assert "- lifecycle_action: adopt" in packet["project_start_issue"]["body"]


def test_cli_rejects_invalid_lifecycle_action():
    proc = subprocess.run(
        [
            "python3",
            str(MODULE_PATH),
            "--cwd",
            str(REPO_ROOT),
            "--json",
            "--lifecycle-action",
            "archive",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode != 0
    assert "invalid choice" in proc.stderr


def test_cli_requires_template_selection_flags():
    proc = subprocess.run(
        [
            "python3",
            str(MODULE_PATH),
            "--cwd",
            str(REPO_ROOT),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode != 0
    assert "--template-id" in proc.stderr


def test_cli_rejects_invalid_ui_impact():
    proc = subprocess.run(
        [
            "python3",
            str(MODULE_PATH),
            "--cwd",
            str(REPO_ROOT),
            "--json",
            "--template-id",
            "test-erik-project-template",
            "--template-version",
            "v1",
            "--deploy-profile",
            "preview-dev-prod-monorepo",
            "--override-scope",
            "customer-config-only",
            "--lifecycle-action",
            "adopt",
            "--ui-impact",
            "maybe",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode != 0
    assert "invalid choice" in proc.stderr


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
