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


def first_text_block_after(text: str, marker: str) -> str:
    marker_index = text.index(marker)
    fence_start = text.index("```text", marker_index)
    block_start = fence_start + len("```text\n")
    block_end = text.index("```", block_start)
    return text[block_start:block_end]


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
    assert repo_bootstrap["target_repo_visibility"] == "public-when-created"
    assert "GitHub Free organization rulesets" in repo_bootstrap["visibility_reason"]
    assert "public" in repo_bootstrap["visibility_reason"]


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
        {
            "source_template": (
                "clever-agent-project/docs/templates/apply-target-repo-rulesets.sh"
            ),
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
            "source_template": (
                "clever-agent-project/docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md"
            ),
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
    assert packet["repo_bootstrap"]["local_folder_layout"] == {
        "control_plane_root": "<CLEVER_ROOT>/clever-agent-workspace",
        "control_plane_repositories": [
            "clever-agent-project",
            "clever-context-monorepo",
            "clever-change-control",
        ],
        "project_repositories_root": "<CLEVER_ROOT>/projects/<project-slug>",
        "target_repo_checkout": "<CLEVER_ROOT>/projects/<project-slug>/<target-repo>",
        "seed_injection_root": "target repo root",
    }
    assert (
        "copy target repo seed files into the target repo root before handoff"
        in packet["repo_bootstrap"]["post_create_clone"]
    )
    assert any(
        "<CLEVER_ROOT>/projects/<project-slug>/<target-repo>" in step
        for step in packet["repo_bootstrap"]["post_create_clone"]
    )
    assert (
        "apply GitHub rulesets after dev exists"
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


def test_control_plane_docs_define_projects_folder_layout():
    docs = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs/setting.md",
        REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md",
    ]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        assert "<CLEVER_ROOT>/" in text
        assert "clever-agent-workspace/" in text
        assert "clever-agent-project/" in text
        assert "clever-context-monorepo/" in text
        assert "clever-change-control/" in text
        assert "projects/" in text
        assert "<project-slug>/" in text
        assert "<target-repo>/" in text

    setting = (REPO_ROOT / "docs/setting.md").read_text(encoding="utf-8")
    assert "3대 레포는 항상 그 안의 sibling" in setting
    assert "target repo 루트에 주입" in setting


def test_target_repo_agents_template_enforces_github_development_branch_flow():
    agents_template = REPO_ROOT / "docs/templates/target-repo-AGENTS.md"

    agents = agents_template.read_text(encoding="utf-8")

    assert "GitHub issue-linked branch 생성" in agents
    assert "gh issue develop <target-issue-number>" in agents
    assert "--base dev" in agents
    assert "--name cc-<change-control-issue-number>-<short-scope>" in agents
    assert "--checkout" in agents
    assert "gh issue develop --list <target-issue-number>" in agents
    assert "EVNSolution/thundercrew-domain" in agents
    assert "git checkout -b" in agents
    assert "## 브랜치 이름 규칙" in agents
    assert "cc-74-dashboard-mapstate-frontend" in agents
    assert "GitHub Issue Development에 연결되지 않은 branch" in agents
    assert "Co-authored-by: OmX" in agents
    assert "cat > .git/hooks/pre-commit <<'EOF'" in agents
    assert "cat > .git/hooks/pre-push <<'EOF'" in agents
    assert "cc-[0-9]*-*" in agents


def test_target_repo_agents_template_enforces_pr_validation_and_report_contract():
    agents = (REPO_ROOT / "docs/templates/target-repo-AGENTS.md").read_text(
        encoding="utf-8"
    )

    assert "PR은 작업 branch에서 `dev`로 생성한다" in agents
    assert "PR 본문에는 target issue와" in agents
    assert "npm run check:workspace" in agents
    assert "npm run lint" in agents
    assert "npm run typecheck" in agents
    assert "npm run build" in agents
    assert "npm run test:service-ops" in agents
    assert "cd development/service-ops-api && ./gradlew test" in agents
    assert "cd development/service-ops-api && ./gradlew build" in agents
    for expected in [
        "target issue 번호",
        "change-control issue 번호",
        "linked branch 이름",
        "PR 번호",
        "merge commit",
        "검증 명령 결과",
        "남은 후속 작업",
    ]:
        assert expected in agents


def test_root_prompts_enforce_issue_linked_target_workflow():
    root_agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md").read_text(
        encoding="utf-8"
    )

    for text in [root_agents, skill]:
        assert "gh issue develop <target-issue-number>" in text
        assert "--repo <target-repo-full-name>" in text
        assert "--base dev" in text
        assert "--name cc-<change-control-issue-number>-<short-scope>" in text
        assert "gh issue develop --list <target-issue-number>" in text
        assert "git checkout -b" in text
        assert "Do not implement, commit, or open a PR" in text or "may the agent implement, commit, or open a PR" in text


def test_target_repo_ruleset_template_applies_main_and_dev_only():
    ruleset_template = REPO_ROOT / "docs/templates/apply-target-repo-rulesets.sh"
    agents_template = REPO_ROOT / "docs/templates/target-repo-AGENTS.md"

    ruleset_script = ruleset_template.read_text(encoding="utf-8")
    agents = agents_template.read_text(encoding="utf-8")

    assert "gh api" in ruleset_script
    assert "CLEVER protect main" in ruleset_script
    assert "CLEVER protect dev" in ruleset_script
    assert "visibility" in ruleset_script
    assert "PUBLIC" in ruleset_script
    assert "GitHub Free organization rulesets require a public repository" in ruleset_script
    assert '"include":["refs/heads/main"]' in ruleset_script
    assert '"include":["refs/heads/dev"]' in ruleset_script
    assert ruleset_script.count('"required_approving_review_count":0') == 2
    assert '"required_approving_review_count":1' not in ruleset_script
    assert "refs/heads/*" not in ruleset_script
    assert "~ALL" not in ruleset_script
    assert "main: PR 경유만 허용" in agents
    assert "dev: PR 경유만 허용" in agents
    assert "승인 수는 둘 다 0명" in agents
    assert "그 외 branch: GitHub ruleset 미적용" in agents
    assert "새 프로젝트 repo는 public으로 만든다" in agents


def test_docs_require_remote_task_branch_cleanup_after_pr_completion():
    docs = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md",
        REPO_ROOT / "docs/setting.md",
        REPO_ROOT / "docs/templates/target-repo-AGENTS.md",
    ]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        assert "PR 완료 후 branch 정리" in text
        assert text.count("PR 완료 후 branch 정리") == 1
        assert "git push origin --delete <source-branch>" in text
        assert "git branch -d <source-branch>" in text
        assert "main`과 `dev`는 삭제 대상이 아니다" in text
        assert "open PR" in text


def test_target_repo_agents_prompts_next_issue_template_after_main_cleanup():
    agents = (REPO_ROOT / "docs/templates/target-repo-AGENTS.md").read_text(
        encoding="utf-8"
    )

    assert "### 다음 작업 이슈 생성 템플릿" in agents
    assert "main merge" in agents
    assert "이슈/브랜치 정리" in agents
    assert "다음 작업을 시작하기 전에" in agents
    assert "[이슈 요약]:" in agents
    assert "[이슈 내용]:" in agents
    assert "[완료 기준]:" in agents
    assert "- [ ]" in agents
    assert "사용자가 작성한 템플릿이나 기존 issue URL" in agents


def test_first_main_push_requires_root_agents_seed_confirmation():
    docs = [
        (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        (REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md").read_text(
            encoding="utf-8"
        ),
        (REPO_ROOT / "docs/templates/target-repo-AGENTS.md").read_text(
            encoding="utf-8"
        ),
        (REPO_ROOT / "docs/setting.md").read_text(encoding="utf-8"),
    ]

    for text in docs:
        assert "첫 main push" in text
        assert "루트 `AGENTS.md`" in text
        assert "docs/templates/target-repo-AGENTS.md" in text
        assert "push하지 않는다" in text


def test_target_repo_pr_template_makes_review_finish_with_wiki_update():
    pr_template = (
        REPO_ROOT / "docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md"
    ).read_text(encoding="utf-8")
    agents = (REPO_ROOT / "docs/templates/target-repo-AGENTS.md").read_text(
        encoding="utf-8"
    )
    setting = (REPO_ROOT / "docs/setting.md").read_text(encoding="utf-8")
    issue_prompt = (
        REPO_ROOT / "docs/templates/issue-resolution-context-wiki-prompt.md"
    ).read_text(encoding="utf-8")
    main_prompt = (
        REPO_ROOT / "docs/templates/main-pr-global-context-wiki-prompt.md"
    ).read_text(encoding="utf-8")

    assert "CLEVER PR review completion" in pr_template
    assert "target branch: `dev` / `main`" in pr_template
    assert "검토 에이전트 작업은 wiki/service context 업데이트로 마친다" in pr_template
    assert "PR 정보를 wiki에 올리지 않는다" in pr_template
    assert "wiki/service context update result" in pr_template
    assert "clever-context-monorepo update" in pr_template
    assert "linked issue close evidence" in pr_template
    assert "이슈 종료는 PR 검토 완료 결과를 근거로 처리한다" in pr_template
    assert "PR 완료 후 branch 정리" not in pr_template
    assert "git push origin --delete <source-branch>" not in pr_template
    assert "git branch -d <source-branch>" not in pr_template

    assert "PR 검토 에이전트 종료 조건" in agents
    assert "wiki/service context 업데이트로 마친다" in agents
    assert "PR 정보를 wiki에 올리지 않는다" in agents
    assert "이슈 종료는 PR 검토 완료 결과를 근거로 처리한다" in agents
    assert "완료 commit" in agents
    assert "git push origin --delete <source-branch>" in agents
    assert "git branch -d <source-branch>" in agents

    assert "dev/main PR review completion" in setting
    assert "검토 에이전트 작업은 wiki/service context 업데이트로 끝난다" in setting
    assert "이슈 종료는 PR 검토 완료 결과를 참조한다" in setting
    assert "PR 검토 에이전트 작업은 wiki/service context 업데이트로 마친다" in issue_prompt
    assert "이번 작업은 PR merge 단위다" in main_prompt
    assert "PR 정보를 wiki에 올리지 않는다" in main_prompt
    assert "`dev` 또는 `main`" in main_prompt


def test_agent_project_agents_file_is_clone_ready_for_startup_questions():
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Clone-Ready Startup Contract" in agents
    assert "fresh clone" in agents
    assert "작업 시작 질문을 남긴다" in agents
    assert "질문 원장" in agents
    assert "known answer" in agents
    assert "needs-input" in agents
    assert "python3 scripts/bootstrap_clever_work.py --cwd \"$PWD\" --preflight --json" in agents
    assert "작업 성격은 어디에 가깝나요?" in agents
    assert "신규 개발" in agents
    assert "버그 수정" in agents
    assert "대상 범위는 무엇인가요?" in agents
    assert "CI/CD 또는 배포 workflow" in agents
    assert "전문 용어" in agents
    assert "양식을 채워도 되고, 자연어로 편하게 설명해도 된다" in agents
    assert "자연어 입력 처리 규칙" in agents


def test_readme_exposes_copyable_first_clone_command_box():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## 1분 설치" not in readme
    assert "## 빠른 시작" not in readme
    assert "## 사용 환경별 시작" in readme
    assert readme.index("## 사용 환경별 시작") < readme.index("```bash\nmkdir -p clever-agent-workspace")
    assert "## How to Start" not in readme
    assert "## 시작 입력" in readme
    assert "## 운영 세부 기준" not in readme
    assert "## 워크스페이스 레포지토리" not in readme
    assert "## 빠른 링크" not in readme
    assert "## CLEVER란 무엇인가" not in readme
    assert "## 왜 3개 레포가 모두 필요한가" not in readme
    assert "## 필수 워크스페이스 계약" not in readme
    assert "## 레포 맵" not in readme
    assert "## 시나리오 다이어그램" not in readme
    assert "## 상세 문서" not in readme
    assert "## 관련 레포" not in readme
    assert "터미널 CLI용 직접 설정 명령" in readme
    assert "아래 명령은 터미널 CLI 사용자를 위한 직접 설정용이다" in readme
    assert "```bash\nmkdir -p clever-agent-workspace" in readme
    assert "git clone https://github.com/EVNSolution/clever-agent-project.git" in readme
    assert "git clone https://github.com/EVNSolution/clever-context-monorepo.git" in readme
    assert "git clone https://github.com/EVNSolution/clever-change-control.git" in readme
    assert readme.count("git clone https://github.com/EVNSolution/clever-agent-project.git") == 3
    assert readme.count("git clone https://github.com/EVNSolution/clever-context-monorepo.git") == 3
    assert readme.count("git clone https://github.com/EVNSolution/clever-change-control.git") == 3
    assert "cd clever-agent-project" in readme
    assert 'CLEVER_EXPECTED_GITHUB_LOGIN="<github-login-or-profile-url>" \\\n  python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json' in readme
    assert "python3 scripts/bootstrap_clever_work.py --cwd \"$PWD\" --preflight --json" in readme
    assert "에이전트 종류별 실행 예시" in readme
    assert "codex --yolo" in readme
    assert "claude --dangerously-skip-permissions" in readme
    assert "gemini --yolo" in readme
    assert "```text\n작업 시작" in readme
    assert "아래 양식을 채워도 되고, 자연어로 편하게 설명해도 된다" in readme
    assert "혹은 자연어로 편하게 대화하며 진행하세요" in readme
    assert readme.count("아래 양식을 채워도 되고, 자연어로 편하게 설명해도 된다") == 1
    assert readme.count("혹은 자연어로 편하게 대화하며 진행하세요") == 1
    assert "자연어 예시" in readme


def test_build_packet_includes_post_create_clone_and_handoff_plan():
    packet = build_packet()

    repo_bootstrap = packet["repo_bootstrap"]
    handoff = packet["repo_session_handoff"]

    assert repo_bootstrap["post_create_clone"] == [
        "create-or-confirm public target repo after project-start approval",
        "clone-or-pull the target repo under <CLEVER_ROOT>/projects/<project-slug>/<target-repo>",
        "copy target repo seed files into the target repo root before handoff",
        "apply GitHub rulesets after dev exists",
        "verify local checkout is ready for follow-on work",
    ]
    assert repo_bootstrap["local_folder_layout"]["target_repo_checkout"] == (
        "<CLEVER_ROOT>/projects/<project-slug>/<target-repo>"
    )
    assert handoff["recommended_session"] == "new-target-repo-session"
    assert handoff["status"] == "recommended-after-clone"
    assert "Switch to the cloned target repo" in handoff["summary"]
    assert "seed AGENTS.md and docs/project-brief.md" in handoff["summary"]
    assert "projects folder" in packet["next_step"]
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


def test_readme_and_setting_document_public_target_repo_visibility_rule():
    setting = (REPO_ROOT / "docs/setting.md").read_text(encoding="utf-8")
    skill = (REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "새 target repo는 public으로 생성한다" in setting
    assert "GitHub Free 조직에서 private repo ruleset이 enforce되지 않는다" in setting
    assert "gh repo create <owner>/<repo> --public" in setting
    assert "새 target repo는 public으로 생성한다" in skill


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


def test_preflight_check_passes_when_github_account_workspace_and_remotes_are_ready(
    monkeypatch,
):
    module = load_module()
    command_log: list[tuple[str, ...]] = []

    def fake_which(name: str) -> str | None:
        return f"/usr/bin/{name}" if name in {"git", "gh"} else None

    def fake_workspace_check(cwd: Path, *, current_repo_maintenance: bool = False):
        return {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {
                "clever-agent-project": {"checkout_path": "/workspace/clever-agent-project"},
                "clever-context-monorepo": {
                    "checkout_path": "/workspace/clever-context-monorepo"
                },
                "clever-change-control": {"checkout_path": "/workspace/clever-change-control"},
            },
        }

    def fake_run(cmd: list[str], cwd: Path | None = None):
        command_log.append(tuple(cmd))
        if cmd[:3] == ["gh", "api", "user"]:
            return module.CommandResult(0, "jiinlim\n", "")
        if cmd[:3] == ["gh", "api", "user/memberships/orgs/EVNSolution"]:
            return module.CommandResult(0, json.dumps({"state": "active", "role": "admin"}), "")
        if cmd[:2] == ["gh", "auth"]:
            return module.CommandResult(0, "Logged in to github.com as jiinlim\n", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-agent-project"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-agent-project.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-context-monorepo"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-context-monorepo.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-change-control"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-change-control.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["gh", "repo", "view"]:
            return module.CommandResult(
                0,
                json.dumps(
                    {
                        "nameWithOwner": cmd[3],
                        "visibility": "PUBLIC",
                        "isPrivate": False,
                        "viewerPermission": "ADMIN",
                    }
                ),
                "",
            )
        if cmd[:2] == ["gh", "issue"]:
            return module.CommandResult(0, "[]\n", "")
        if cmd[:2] == ["gh", "pr"]:
            return module.CommandResult(0, "[]\n", "")
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/rulesets"):
            return module.CommandResult(0, "[]\n", "")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(module.shutil, "which", fake_which)
    monkeypatch.setattr(module, "build_workspace_check", fake_workspace_check)
    monkeypatch.setattr(module, "run_command_result", fake_run)

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login="jiinlim",
        github_owner="EVNSolution",
    )

    assert report["ready"] is True
    assert report["mode"] == "basic"
    assert report["github_login"] == "jiinlim"
    assert {check["name"]: check["status"] for check in report["checks"]} == {
        "git-cli": "pass",
        "gh-cli": "pass",
        "gh-auth": "pass",
        "github-account": "pass",
        "github-org-membership": "pass",
        "workspace": "pass",
        "control-plane-remotes": "pass",
        "control-plane-worktrees-clean": "pass",
        "control-plane-remote-fetch": "pass",
        "github-repo-access": "pass",
        "github-issue-pr-access": "pass",
        "ruleset-read": "pass",
    }
    assert ("gh", "api", "user", "--jq", ".login") in command_log


def test_preflight_check_reports_auto_skips_and_next_startup_question(monkeypatch):
    module = load_module()

    def fake_workspace_check(cwd: Path, *, current_repo_maintenance: bool = False):
        return {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "current_repo": "clever-agent-project",
            "current_repo_is_start": True,
            "control_plane_complete": True,
            "repos": {
                "clever-agent-project": {"checkout_path": "/workspace/clever-agent-project"},
                "clever-context-monorepo": {
                    "checkout_path": "/workspace/clever-context-monorepo"
                },
                "clever-change-control": {"checkout_path": "/workspace/clever-change-control"},
            },
        }

    def fake_run(cmd: list[str], cwd: Path | None = None):
        if cmd[:3] == ["gh", "api", "user"]:
            return module.CommandResult(0, "jiinlim\n", "")
        if cmd[:3] == ["gh", "api", "user/memberships/orgs/EVNSolution"]:
            return module.CommandResult(0, json.dumps({"state": "active", "role": "admin"}), "")
        if cmd[:2] == ["gh", "auth"]:
            return module.CommandResult(0, "Logged in to github.com as jiinlim\n", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-agent-project"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-agent-project.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-context-monorepo"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-context-monorepo.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["git", "-C", "/workspace/clever-change-control"]:
            if cmd[3:] == ["remote", "get-url", "origin"]:
                return module.CommandResult(
                    0, "https://github.com/EVNSolution/clever-change-control.git\n", ""
                )
            if cmd[3:] == ["status", "--short"]:
                return module.CommandResult(0, "", "")
            if cmd[3:] == ["fetch", "--dry-run", "origin"]:
                return module.CommandResult(0, "", "")
        if cmd[:3] == ["gh", "repo", "view"]:
            return module.CommandResult(
                0,
                json.dumps(
                    {
                        "nameWithOwner": cmd[3],
                        "visibility": "PUBLIC",
                        "isPrivate": False,
                        "viewerPermission": "ADMIN",
                    }
                ),
                "",
            )
        if cmd[:2] == ["gh", "issue"]:
            return module.CommandResult(0, "[]\n", "")
        if cmd[:2] == ["gh", "pr"]:
            return module.CommandResult(0, "[]\n", "")
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/rulesets"):
            return module.CommandResult(0, "[]\n", "")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(module, "build_workspace_check", fake_workspace_check)
    monkeypatch.setattr(module, "run_command_result", fake_run)

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login=None,
        github_owner="EVNSolution",
    )

    assert report["ready"] is True
    assert report["recovery_actions"] == []
    assert report["auto_skipped_questions"] == [
        {
            "question": "github_login",
            "reason": "gh CLI inferred the authenticated GitHub account.",
            "evidence": "jiinlim",
        },
        {
            "question": "startup_location",
            "reason": "workspace_check.agent_action already selected the startup path.",
            "evidence": "proceed-with-hard-gate",
        },
        {
            "question": "dirty_state",
            "reason": "control-plane worktree cleanliness was checked automatically.",
            "evidence": "pass",
        },
    ]
    assert report["next_questions"] == [
        {
            "id": "startup_branch_input",
            "prompt": "작업 시작: 먼저 하려는 일을 한 줄로 적어 주세요.",
            "reason": "preflight passed and the workspace is ready for the startup template.",
        }
    ]


def test_preflight_check_infers_github_login_from_gh_cli_when_expected_missing(monkeypatch):
    module = load_module()

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "build_workspace_check",
        lambda cwd, *, current_repo_maintenance=False: {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {},
        },
    )

    def fake_run(cmd, cwd=None):
        if cmd[:3] == ["gh", "api", "user"]:
            return module.CommandResult(0, "jiinlim\n", "")
        if cmd == ["gh", "api", "user/memberships/orgs/EVNSolution"]:
            return module.CommandResult(0, json.dumps({"state": "active"}), "")
        return module.CommandResult(0, "", "")

    monkeypatch.setattr(module, "run_command_result", fake_run)

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login=None,
        github_owner="EVNSolution",
    )

    assert report["ready"] is False
    assert report["expected_github_login"] is None
    assert report["github_login"] == "jiinlim"
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["github-account"]["status"] == "pass"
    assert checks["github-account"]["message"] == "GitHub account inferred from gh CLI: jiinlim."
    assert "Ask the user for their GitHub login or profile URL" not in checks["github-account"][
        "message"
    ]
    assert {
        "question": "github_login",
        "reason": "gh CLI inferred the authenticated GitHub account.",
        "evidence": "jiinlim",
    } in report["auto_skipped_questions"]
    assert "OziinG" not in checks["github-account"]["message"]


def test_preflight_check_asks_for_github_login_only_when_gh_cli_cannot_infer_account(
    monkeypatch,
):
    module = load_module()

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "build_workspace_check",
        lambda cwd, *, current_repo_maintenance=False: {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {},
        },
    )

    def fake_run(cmd, cwd=None):
        if cmd[:3] == ["gh", "api", "user"]:
            return module.CommandResult(1, "", "not logged in")
        return module.CommandResult(0, "", "")

    monkeypatch.setattr(module, "run_command_result", fake_run)

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login=None,
        github_owner="EVNSolution",
    )

    assert report["ready"] is False
    assert report["github_login"] is None
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["github-account"]["status"] == "fail"
    assert "Cannot infer GitHub account from gh CLI" in checks["github-account"][
        "message"
    ]
    assert "Ask the user for their GitHub login or profile URL" in checks[
        "github-account"
    ]["message"]
    assert {
        "check": "github-account",
        "action": "Run gh auth login or provide the GitHub login/profile URL to use as an override.",
        "command": "gh auth login",
    } in report["recovery_actions"]
    assert report["next_questions"][0] == {
        "id": "github_login",
        "prompt": "GitHub login 또는 profile URL을 알려 주세요.",
        "reason": "gh CLI could not infer the authenticated account.",
    }
    assert "OziinG" not in checks["github-account"]["message"]


def test_preflight_check_accepts_expected_github_profile_url(monkeypatch):
    module = load_module()

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "build_workspace_check",
        lambda cwd, *, current_repo_maintenance=False: {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {},
        },
    )
    monkeypatch.setattr(
        module,
        "run_command_result",
        lambda cmd, cwd=None: module.CommandResult(
            0,
            "jiinlim\n" if cmd[:3] == ["gh", "api", "user"] else "",
            "",
        ),
    )

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login="https://github.com/jiinlim",
        github_owner="EVNSolution",
    )

    assert report["github_login"] == "jiinlim"
    assert report["expected_github_login"] == "jiinlim"
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["github-account"]["status"] == "pass"


def test_preflight_check_fails_before_startup_when_github_login_is_wrong(monkeypatch):
    module = load_module()

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "build_workspace_check",
        lambda cwd, *, current_repo_maintenance=False: {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {},
        },
    )
    monkeypatch.setattr(
        module,
        "run_command_result",
        lambda cmd, cwd=None: module.CommandResult(
            0,
            "other-user\n" if cmd[:3] == ["gh", "api", "user"] else "",
            "",
        ),
    )

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login="jiinlim",
        github_owner="EVNSolution",
    )

    assert report["ready"] is False
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["github-account"]["status"] == "fail"
    assert "jiinlim" in checks["github-account"]["message"]
    assert "other-user" in checks["github-account"]["message"]


def test_admin_preflight_requires_admin_permission_for_target_repo(monkeypatch):
    module = load_module()

    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "build_workspace_check",
        lambda cwd, *, current_repo_maintenance=False: {
            "startup_ready": True,
            "agent_action": "proceed-with-hard-gate",
            "repos": {},
        },
    )

    def fake_run(cmd: list[str], cwd: Path | None = None):
        if cmd[:2] == ["gh", "auth"]:
            return module.CommandResult(0, "Logged in\n", "")
        if cmd[:3] == ["gh", "api", "user"]:
            return module.CommandResult(0, "jiinlim\n", "")
        if cmd[:3] == ["gh", "api", "user/memberships/orgs/EVNSolution"]:
            return module.CommandResult(0, json.dumps({"state": "active", "role": "admin"}), "")
        if cmd[:3] == ["gh", "repo", "view"]:
            return module.CommandResult(
                0,
                json.dumps(
                    {
                        "nameWithOwner": cmd[3],
                        "visibility": "PUBLIC",
                        "isPrivate": False,
                        "viewerPermission": "WRITE",
                    }
                ),
                "",
            )
        if cmd[:2] == ["gh", "issue"] or cmd[:2] == ["gh", "pr"]:
            return module.CommandResult(0, "[]\n", "")
        if cmd[:2] == ["gh", "api"] and cmd[2].endswith("/rulesets"):
            return module.CommandResult(0, "[]\n", "")
        if cmd[:1] == ["git"]:
            return module.CommandResult(0, "", "")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(module, "run_command_result", fake_run)

    report = module.build_preflight_check(
        cwd=REPO_ROOT,
        expected_github_login="jiinlim",
        github_owner="EVNSolution",
        admin=True,
        target_repo_full_name="EVNSolution/example-target",
    )

    assert report["ready"] is False
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["target-repo-admin"]["status"] == "fail"
    assert "ADMIN" in checks["target-repo-admin"]["message"]


def test_docs_require_preflight_before_startup_and_admin_repo_bootstrap():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md").read_text(
        encoding="utf-8"
    )
    target_agents = (REPO_ROOT / "docs/templates/target-repo-AGENTS.md").read_text(
        encoding="utf-8"
    )

    assert "--preflight" in readme
    assert "GitHub 계정" in readme
    assert "CLEVER_EXPECTED_GITHUB_LOGIN" in readme
    assert "gh CLI에서 GitHub 계정이 확인되면 별도로 묻지 않는다" in readme
    assert "내 GitHub login 또는 profile URL을 먼저 물어봐줘" not in readme
    assert "OziinG" not in readme
    assert "--admin-preflight" not in readme

    for text in (agents, skill):
        assert "--preflight" in text
        assert "gh auth status" in text
        assert "GitHub login" in text
        assert "CLEVER_EXPECTED_GITHUB_LOGIN" in text
        assert "infer the GitHub account from gh CLI first" in text
        assert "ask the current user for their GitHub login or profile URL, then run" not in text
        assert "OziinG" not in text
        assert "--admin-preflight" in text
    assert "OziinG" not in target_agents
    assert "Preflight Gate" in target_agents
    assert "team-work automation" in target_agents


def test_docs_describe_preflight_auto_skips_recovery_actions_and_next_questions():
    docs = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md",
        REPO_ROOT / "docs/setting.md",
        REPO_ROOT / "docs/guides/session-start-smoke-test.md",
    ]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        assert "auto_skipped_questions" in text
        assert "recovery_actions" in text
        assert "next_questions" in text


def test_readme_guides_non_expert_users_by_entry_surface():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "## 사용 환경별 시작" in readme
    assert readme.count("<details>") >= 3
    assert readme.count("</details>") >= 3
    assert "<summary><strong>앱형 에이전트 / Application</strong> — 채팅에 프롬프트를 붙여 넣고 기본 세팅을 맡긴다.</summary>" in readme
    assert "<summary><strong>VS Code Extension</strong> — 확장 채팅과 Integrated Terminal로 기본 세팅을 맡긴다.</summary>" in readme
    assert "<summary><strong>터미널 CLI</strong> — 개발자처럼 직접 작업 디렉토리에서 시작한다.</summary>" in readme
    assert readme.index("앱형 에이전트 / Application</strong>") < readme.index("터미널 CLI</strong>")
    assert readme.index("VS Code Extension</strong>") < readme.index("터미널 CLI</strong>")
    for surface in [
        "앱형 에이전트",
        "터미널 CLI",
        "VS Code Extension",
    ]:
        assert surface in readme
    assert "터미널 CLI는 개발자처럼 직접 작업 디렉토리에서 시작한다" in readme
    assert "앱형 에이전트는 LLM과 대화하듯이 세팅을 맡긴다" in readme
    assert "VS Code Extension도 확장 채팅에 세팅을 맡긴다" in readme
    assert "아래 프롬프트를 그대로 붙여 넣는다" in readme
    assert "gh CLI에서 계정을 확인할 수 있으면 별도로 묻지 말고" in readme
    assert "GitHub 계정을 확인할 수 없거나 다른 계정을 써야 할 때만 물어봐줘" in readme
    assert "3개 repo가 있는지 확인하고, 없는 repo만" in readme
    assert "필요한 shell 명령은 네가 실행하고 결과를 확인해줘" in readme
    assert "Integrated Terminal" in readme

    app_prompt = first_text_block_after(readme, "앱형 에이전트 / Application")
    vscode_prompt = first_text_block_after(readme, "VS Code Extension")
    for prompt in (app_prompt, vscode_prompt):
        assert "3개 repo가 있는지 확인하고, 없는 repo만" in prompt
        assert "mkdir -p clever-agent-workspace" in prompt
        assert "git clone https://github.com/EVNSolution/clever-agent-project.git" in prompt
        assert "git clone https://github.com/EVNSolution/clever-context-monorepo.git" in prompt
        assert "git clone https://github.com/EVNSolution/clever-change-control.git" in prompt
        assert 'python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json' in prompt


def test_startup_first_questions_prioritize_project_and_service_scope():
    docs = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md",
        REPO_ROOT / "docs/templates/startup-branch-state-template.md",
        REPO_ROOT / "docs/setting.md",
        REPO_ROOT / "docs/guides/session-start-smoke-test.md",
    ]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        assert "먼저 하려는 일을 한 줄로 적어 주세요" in text
        assert "작업 성격은 어디에 가깝나요?" in text
        assert "신규 개발" in text
        assert "기존 기능 확장/수정" in text
        assert "버그 수정" in text
        assert "리팩터링/구조 개선" in text
        assert "대상 범위는 무엇인가요?" in text
        assert "CI/CD 또는 배포 workflow" in text
        assert "현재 상태를 알고 있나요?" in text
        assert "모르면 `아직 모름`" in text


def test_startup_visible_template_uses_actionable_non_expert_questions():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (
        REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md"
    ).read_text(encoding="utf-8")
    startup_template = (
        REPO_ROOT / "docs/templates/startup-branch-state-template.md"
    ).read_text(encoding="utf-8")

    visible_blocks = [
        first_text_block_after(readme, "## 시작 입력"),
        first_text_block_after(agents, "If the user has not already provided"),
        first_text_block_after(skill, "Use this exact first-response template"),
        first_text_block_after(startup_template, "## 사용자에게 보여주는 입력 양식"),
    ]

    for block in visible_blocks:
        assert "하려는 일:" in block
        assert "작업 성격은 어디에 가깝나요?" in block
        assert "대상 범위는 무엇인가요?" in block
        assert "이번 작업의 목표 수준은 어디까지인가요?" in block
        assert "현재 상태를 알고 있나요?" in block
        assert "건드리면 안 되는 범위" in block
        assert "보안/운영/배포 관련 주의사항" in block
        assert "알고 있는 이름이나 링크" in block
        assert "주의할 점" in block
        assert "직접 설명:" in block
        assert "MONO" not in block
        assert "MSA" not in block
        assert "target_service" not in block
        assert "프로젝트 상태:" not in block
        assert "서비스 범위:" not in block
        assert "이번 세션 목표:" not in block
        assert "왜 필요한지" not in block
        assert "기대 결과" not in block


def test_process_docs_stay_synced_with_current_startup_language():
    docs = [
        REPO_ROOT / "docs/diagrams/README.md",
        REPO_ROOT / "docs/diagrams/clever-work-lifecycle.md",
        REPO_ROOT / "docs/diagrams/clever-work-lifecycle.html",
        REPO_ROOT / "docs/diagrams/clever-control-plane-overview.html",
        REPO_ROOT / "docs/guides/clever-project-workflows.md",
    ]
    stale_phrases = [
        "3단계 시작 템플릿",
        "three-step opening template",
        "작업 유형 + MSA/MONO",
        "새 서비스 개발 vs. 기존 서비스 추가",
        "추가 설명: 목적, 제약, 기대 결과",
        "모든 경우에 아래 규칙은 공통이다.\n\n1. 시작은 `clever-agent-project`에서 한다.",
        "candidate template lineage",
    ]

    for doc_path in docs:
        text = doc_path.read_text(encoding="utf-8")
        for phrase in stale_phrases:
            assert phrase not in text, f"{doc_path} still contains {phrase!r}"

    lifecycle = (REPO_ROOT / "docs/diagrams/clever-work-lifecycle.md").read_text(
        encoding="utf-8"
    )
    workflows = (REPO_ROOT / "docs/guides/clever-project-workflows.md").read_text(
        encoding="utf-8"
    )

    assert "작업 성격 + 대상 범위 + 목표 수준" in lifecycle
    assert "generic startup은 `clever-agent-project`에서 시작한다" in workflows


def test_agent_files_startup_behavior_uses_preflight_gate():
    agent_files = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs/templates/target-repo-AGENTS.md",
    ]

    for doc_path in agent_files:
        text = doc_path.read_text(encoding="utf-8")
        assert "Run the workspace check" not in text
        assert "automatic workspace check" not in text
        assert "preflight_check.ready=true" in text


def test_sibling_control_plane_agent_files_point_to_agent_project_for_startup():
    sibling_agent_files = [
        REPO_ROOT.parent / "clever-context-monorepo/AGENTS.md",
        REPO_ROOT.parent / "clever-change-control/AGENTS.md",
    ]

    for doc_path in sibling_agent_files:
        text = doc_path.read_text(encoding="utf-8")
        assert "startup/preflight authority lives in `clever-agent-project`" in text
        assert "python3 ../clever-agent-project/scripts/bootstrap_clever_work.py" not in text
        assert "CLEVER_EXPECTED_GITHUB_LOGIN" not in text
        assert "gh auth status" not in text
        assert "workspace_check.agent_action" not in text


def test_context_governance_keeps_startup_details_in_agent_project():
    text = (REPO_ROOT.parent / "clever-context-monorepo/docs/root/agent-runtime-governance.md").read_text(
        encoding="utf-8"
    )

    assert "startup/preflight authority lives in `clever-agent-project`" in text
    assert "python3 ../clever-agent-project/scripts/bootstrap_clever_work.py" not in text
    assert "CLEVER_EXPECTED_GITHUB_LOGIN" not in text
    assert "gh auth status" not in text


def test_startup_guides_use_preflight_command_not_legacy_workspace_cli():
    startup_docs = [
        REPO_ROOT / "docs/guides/session-start-smoke-test.md",
        REPO_ROOT / "docs/guides/three-repo-startup-alignment.md",
        REPO_ROOT / "docs/templates/startup-branch-state-template.md",
    ]

    for doc_path in startup_docs:
        text = doc_path.read_text(encoding="utf-8")
        assert "--workspace-check" not in text
        assert "`workspace-check`" not in text
        assert "workspace check 자동화" not in text
        assert "preflight" in text


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
