from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_readme_links_github_pages_start_wizard():
    readme = read("README.md")

    assert "GitHub Pages 시작 도우미" in readme
    assert "https://evnsolution.github.io/clever-agent-project/start/" in readme
    assert "버튼과 텍스트 입력으로 답한 뒤 최종 copy text" in readme


def test_docs_index_redirects_to_start_wizard():
    index = read("docs/index.html")

    assert "CLEVER 시작 도우미" in index
    assert "url=start/" in index
    assert 'href="start/"' in index


def test_start_wizard_collects_environment_requirements_and_context():
    html = read("docs/start/index.html")

    assert "CLEVER 시작 도우미" in html
    for step in [
        "개발 환경",
        "요구사항",
        "대상 정보",
        "현재 상태",
        "주의사항",
        "copy text",
    ]:
        assert step in html

    for surface in ["Application", "VS Code Extension", "Terminal CLI"]:
        assert surface in html

    for field in [
        "작업 성격",
        "대상 범위",
        "목표 수준",
        "대상 정보",
        "서비스 이름(가칭)",
        "현재 상태",
        "꼭 지킬 것",
        "건드리면 안 되는 범위",
    ]:
        assert field in html


def test_start_wizard_uses_minimal_target_and_state_textareas():
    html = read("docs/start/index.html")

    assert 'id="targetInfo" data-field="targetInfo"' in html
    assert 'id="serviceAlias" data-field="serviceAlias"' in html
    assert 'id="currentState" data-field="currentState"' in html
    assert "기획문서는 있어서 repo만 만들면 바로 시작 가능" in html
    assert "바이브코딩이라 대화로 진행" in html
    assert "다른 MSA 서비스에 있는 기능을 가져와서 새 서비스를 만들거야" in html
    assert "에이전트가 이 내용을 읽고 새 개발인지 기존 서비스 작업인지 판단하세요" in html
    assert "대상 정보 입력" in html
    assert "현재 상태 입력" in html

    removed_detailed_fields = [
        'data-target-card="new"',
        'data-target-card="existing"',
        'function targetInfoMode()',
        'data-field="repo"',
        'data-field="service"',
        'data-field="screen"',
        'data-field="api"',
        'data-field="db"',
        'data-field="docs"',
        'data-field="alreadyDone"',
        'data-field="missing"',
        'data-field="checkFirst"',
    ]
    for removed in removed_detailed_fields:
        assert removed not in html


def test_start_wizard_output_is_clone_ready_and_copyable():
    html = read("docs/start/index.html")

    for repo_url in [
        "https://github.com/EVNSolution/clever-agent-project.git",
        "https://github.com/EVNSolution/clever-context-monorepo.git",
        "https://github.com/EVNSolution/clever-change-control.git",
    ]:
        assert repo_url in html

    assert "test -d clever-agent-project || git clone" in html
    assert 'python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json' in html
    assert "navigator.clipboard.writeText" in html
    assert "copyOutput" in html
    assert "붙여넣어 주세요" in html
    assert "3개 repo가 있는지 확인하고, 없는 repo만 clone" in html


def test_pages_workflow_publishes_docs_directory():
    workflow = read(".github/workflows/pages.yml")

    assert "actions/configure-pages@v6" in workflow
    assert "actions/upload-pages-artifact@v5" in workflow
    assert "actions/deploy-pages@v5" in workflow
    assert "path: docs" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow


def test_pages_workflow_validates_branch_site_before_main_deploy():
    workflow = read(".github/workflows/pages.yml")

    assert "pull_request:" in workflow
    assert "validate:" in workflow
    assert "python3 -m http.server 8000 --directory docs" in workflow
    assert "http://127.0.0.1:8000/" in workflow
    assert "http://127.0.0.1:8000/start/" in workflow
    assert "copyOutput" in workflow
    assert "needs: validate" in workflow
    assert "github.ref == 'refs/heads/main'" in workflow


def test_gitignore_allows_pages_and_wizard_files():
    gitignore = read(".gitignore")

    for pattern in [
        "!/.github/workflows/pages.yml",
        "!/docs/index.html",
        "!/docs/.nojekyll",
        "!/docs/start/",
        "!/docs/start/index.html",
        "!/tests/test_github_pages_start_wizard.py",
    ]:
        assert pattern in gitignore
