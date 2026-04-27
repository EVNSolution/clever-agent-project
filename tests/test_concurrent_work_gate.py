from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGE_CONTROL_ROOT = REPO_ROOT.parent / "clever-change-control"
CONTEXT_ROOT = REPO_ROOT.parent / "clever-context-monorepo"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_agent_rules_define_concurrent_issue_and_pr_gate():
    agent_rules = read(REPO_ROOT / "AGENTS.md")
    target_template = read(REPO_ROOT / "docs/templates/target-repo-AGENTS.md")
    skill = read(REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md")

    for text in (agent_rules, target_template, skill):
        assert "Concurrent Work Gate" in text
        assert "target repo issue" in text
        assert "clever-change-control issue" in text
        assert "open PR" in text
        assert "done" in text
        assert "blocked" in text
        assert "allowed-with-non-overlap" in text
        assert "user-forced-proceed" in text


def test_change_control_rules_record_forced_parallel_work_decisions():
    change_agents = read(CHANGE_CONTROL_ROOT / "AGENTS.md")
    change_request_template = read(
        CHANGE_CONTROL_ROOT / ".github/ISSUE_TEMPLATE/change-request.yml"
    )

    for text in (change_agents, change_request_template):
        assert "Concurrent Work Gate" in text
        assert "user-forced-proceed" in text
        assert "사용자 강제 진행" in text
        assert "conflict candidates" in text
        assert "parallel work decision" in text


def test_pr_templates_require_parallel_work_decision():
    templates = [
        read(REPO_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
        read(REPO_ROOT / "docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md"),
        read(CONTEXT_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
        read(CHANGE_CONTROL_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
    ]

    for text in templates:
        assert "Concurrent Work Gate" in text
        assert "parallel work decision" in text
        assert "conflict candidates" in text
        assert "user-forced-proceed" in text


def test_pr_scope_grouping_guidance_is_documented_and_in_templates():
    shared_policy_surfaces = [
        read(REPO_ROOT / "AGENTS.md"),
        read(REPO_ROOT / "docs/setting.md"),
        read(REPO_ROOT / ".agent/skills/bootstrap-clever-work/SKILL.md"),
        read(REPO_ROOT / "docs/templates/target-repo-AGENTS.md"),
    ]
    context_pipeline_governance = read(
        CONTEXT_ROOT / "docs/root/pipeline-governance.md"
    )
    pr_templates = [
        read(REPO_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
        read(REPO_ROOT / "docs/templates/target-repo-PULL_REQUEST_TEMPLATE.md"),
        read(CONTEXT_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
        read(CHANGE_CONTROL_ROOT / ".github/PULL_REQUEST_TEMPLATE.md"),
    ]

    for text in shared_policy_surfaces + pr_templates:
        assert "PR Scope Grouping Gate" in text
        assert "same document/operating-rule cleanup" in text
        assert "same validation command" in text
        assert "different app/service/contract surface" in text
        assert "merge order dependency" in text
        assert "rollback unit" in text

    assert "PR Scope Grouping Gate" in context_pipeline_governance
    assert "same document/operating-rule cleanup" in context_pipeline_governance
    assert "same validation command" in context_pipeline_governance
    assert "different app/runtime-slice/contract surface" in context_pipeline_governance
    assert "merge order dependency" in context_pipeline_governance
    assert "rollback unit" in context_pipeline_governance
