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


def run_workspace_check(*args, cwd: Path | None = None):
    proc = subprocess.run(
        [
            "python3",
            str(MODULE_PATH),
            "--cwd",
            str(cwd or REPO_ROOT),
            "--workspace-check",
            "--json",
            *args,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return proc, json.loads(proc.stdout)


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
    assert "- The created project-start issue number becomes the root canonical identifier." in draft["body"]
    assert "- Use change id only after approval, when a scoped change request, rollout, or rollback unit has been fixed." in draft["body"]
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


def test_build_workspace_check_reports_ready_from_agent_project():
    module = load_module()

    report = module.build_workspace_check(REPO_ROOT)

    assert report["control_plane_complete"] is True
    assert report["current_repo"] == "clever-agent-project"
    assert report["current_repo_is_start"] is True
    assert report["startup_ready"] is True
    assert report["agent_action"] == "proceed-with-hard-gate"
    assert report["missing_repositories"] == []


def test_build_workspace_check_requires_switch_when_started_from_change_control():
    module = load_module()
    change_repo = REPO_ROOT.parent / "clever-change-control"

    report = module.build_workspace_check(change_repo)

    assert report["control_plane_complete"] is True
    assert report["current_repo"] == "clever-change-control"
    assert report["current_repo_is_start"] is False
    assert report["startup_ready"] is False
    assert report["agent_action"] == "switch-to-clever-agent-project"


def test_build_workspace_check_allows_current_repo_maintenance_when_requested():
    module = load_module()
    change_repo = REPO_ROOT.parent / "clever-change-control"

    report = module.build_workspace_check(change_repo, current_repo_maintenance=True)

    assert report["control_plane_complete"] is True
    assert report["current_repo"] == "clever-change-control"
    assert report["current_repo_maintenance_requested"] is True
    assert report["repo_local_maintenance_candidate"] is True
    assert report["startup_ready"] is True
    assert report["agent_action"] == "current-repo-maintenance"


def test_build_workspace_check_reports_incomplete_workspace(tmp_path: Path):
    module = load_module()
    workspace = tmp_path / "workspace"
    start_repo = workspace / "clever-agent-project"
    start_repo.mkdir(parents=True)

    report = module.build_workspace_check(start_repo)

    assert report["control_plane_complete"] is False
    assert report["startup_ready"] is False
    assert report["agent_action"] == "stop-and-fix-workspace"
    assert "clever-context-monorepo" in report["missing_repositories"]
    assert "clever-change-control" in report["missing_repositories"]


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


def test_build_packet_includes_target_repo_seed_files():
    packet = build_packet(target_repo="clever-analytics-api")

    seed_files = packet["target_repo_seed_files"]

    assert seed_files == [
        {
            "source_template": (
                "clever-agent-project/docs/templates/target-repo-AGENTS.md"
            ),
            "destination": "AGENTS.md",
            "role": "agent execution procedure",
            "purpose": (
                "Define the order, method, checklists, and completion rules "
                "agents must follow in the target repo."
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
            "source_template": (
                "clever-agent-project/docs/templates/target-repo-project-brief.md"
            ),
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
    assert (
        "copy target repo seed files before handoff"
        in packet["repo_bootstrap"]["post_create_clone"]
    )


def test_target_repo_seed_templates_separate_execution_rules_from_project_brief():
    agents_template = REPO_ROOT / "docs/templates/target-repo-AGENTS.md"
    project_brief_template = REPO_ROOT / "docs/templates/target-repo-project-brief.md"

    agents = agents_template.read_text(encoding="utf-8")
    project_brief = project_brief_template.read_text(encoding="utf-8")

    assert "이 파일은 프로젝트 기획서가 아니다" in agents
    assert "작업 시작 순서" in agents
    assert "Branch 운영" in agents
    assert "완료 조건" in agents
    assert "문제 정의" not in agents

    assert "이 파일은 target repo의 초기 기획 초안이다" in project_brief
    assert "문제 정의" in project_brief
    assert "초기 범위" in project_brief
    assert "다음 작업 목록" in project_brief
    assert "agent 작업 절차" in project_brief


def test_target_repo_agents_template_enforces_role_based_branch_prefixes():
    agents_template = REPO_ROOT / "docs/templates/target-repo-AGENTS.md"

    agents = agents_template.read_text(encoding="utf-8")

    assert "브랜치 역할별 접두사" in agents
    for branch_prefix in [
        "feature/",
        "fix/",
        "change/",
        "refactor/",
        "docs/",
        "chore/",
        "test/",
        "release/",
        "hotfix/",
    ]:
        assert branch_prefix in agents
    assert "cat > .git/hooks/pre-commit <<'EOF'" in agents
    assert "cat > .git/hooks/pre-push <<'EOF'" in agents
    assert "main|dev|feature/*|fix/*|change/*|refactor/*|docs/*|chore/*|test/*|release/*|hotfix/*)" in agents
    assert "clever-" in agents


def test_agent_project_agents_file_is_clone_ready_for_startup_questions():
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Clone-Ready Startup Contract" in agents
    assert "fresh clone" in agents
    assert "작업 시작 질문을 남긴다" in agents
    assert "질문 원장" in agents
    assert "known answer" in agents
    assert "needs-input" in agents
    assert "python3 scripts/bootstrap_clever_work.py --cwd \"$PWD\" --workspace-check --json" in agents
    assert "작업 종류" in agents
    assert "구조" in agents
    assert "이번 세션 목표" in agents


def test_readme_exposes_copyable_first_clone_command_box():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## 1분 설치" in readme
    assert "아래 박스를 그대로 복사해서 실행한다" in readme
    assert "```bash\nmkdir -p clever-agent-workspace" in readme
    assert "git clone https://github.com/EVNSolution/clever-agent-project.git" in readme
    assert "git clone https://github.com/EVNSolution/clever-context-monorepo.git" in readme
    assert "git clone https://github.com/EVNSolution/clever-change-control.git" in readme
    assert "cd clever-agent-project" in readme
    assert "python3 scripts/bootstrap_clever_work.py --cwd \"$PWD\" --workspace-check --json" in readme
    assert "```text\n작업 시작" in readme


def test_build_packet_includes_post_create_clone_and_handoff_plan():
    packet = build_packet()

    repo_bootstrap = packet["repo_bootstrap"]
    handoff = packet["repo_session_handoff"]

    assert repo_bootstrap["post_create_clone"] == [
        "create-or-confirm target repo after project-start approval",
        "clone-or-pull the target repo locally",
        "copy target repo seed files before handoff",
        "verify local checkout is ready for follow-on work",
    ]
    assert handoff["recommended_session"] == "new-target-repo-session"
    assert handoff["status"] == "recommended-after-clone"
    assert "Switch to the cloned target repo" in handoff["summary"]
    assert "seed AGENTS.md and docs/project-brief.md" in handoff["summary"]
    assert "seed the target repo" in packet["next_step"]


def test_build_ssot_docs_uses_project_start_aligned_surface():
    module = load_module()
    clever_root = module.find_clever_root(REPO_ROOT)

    docs = module.build_ssot_docs(clever_root)

    assert str(clever_root / "clever-change-control/.github/ISSUE_TEMPLATE/project-start.yml") in docs
    assert str(clever_root / "clever-change-control/changes") in docs
    assert str(clever_root / "clever-change-control/releases") in docs
    assert str(clever_root / "clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml") not in docs
    assert str(clever_root / "clever-context-monorepo/docs/root/authority-boundaries.md") in docs
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


def test_cli_workspace_check_returns_ready_status_in_start_repo():
    proc, payload = run_workspace_check()

    assert proc.returncode == 0
    report = payload["workspace_check"]
    assert report["startup_ready"] is True
    assert report["agent_action"] == "proceed-with-hard-gate"
    assert report["current_repo"] == "clever-agent-project"


def test_cli_workspace_check_allows_current_repo_maintenance_when_flagged():
    change_repo = REPO_ROOT.parent / "clever-change-control"

    proc, payload = run_workspace_check("--current-repo-maintenance", cwd=change_repo)

    assert proc.returncode == 0
    report = payload["workspace_check"]
    assert report["startup_ready"] is True
    assert report["agent_action"] == "current-repo-maintenance"
    assert report["current_repo"] == "clever-change-control"


def test_cli_workspace_check_returns_nonzero_for_incomplete_workspace(tmp_path: Path):
    workspace = tmp_path / "workspace"
    start_repo = workspace / "clever-agent-project"
    start_repo.mkdir(parents=True)

    proc, payload = run_workspace_check(cwd=start_repo)

    assert proc.returncode == 3
    report = payload["workspace_check"]
    assert report["startup_ready"] is False
    assert report["agent_action"] == "stop-and-fix-workspace"
    assert "clever-context-monorepo" in report["missing_repositories"]


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
    assert "change id only after approval" in packet["project_start_issue"]["body"]


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
