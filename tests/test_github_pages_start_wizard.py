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
        "repo",
        "service/app",
        "issue/PR/Figma/회의 메모/에러 로그",
        "꼭 지킬 것",
        "건드리면 안 되는 범위",
    ]:
        assert field in html


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

    assert "actions/configure-pages@v5" in workflow
    assert "actions/upload-pages-artifact@v4" in workflow
    assert "actions/deploy-pages@v4" in workflow
    assert "path: docs" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow


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
