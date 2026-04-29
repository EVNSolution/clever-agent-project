from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def h2_texts(html: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", match).strip() for match in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)]


def test_readme_links_github_pages_start_wizard():
    readme = read("README.md")

    assert "최신 권장 시작점" in readme
    assert "GitHub Pages 시작 도우미" in readme
    assert "https://evnsolution.github.io/clever-agent-project/start/" in readme
    assert "현재 최신 시작 화면" in readme
    assert "README의 긴 양식을 먼저 복사하지 말고" in readme


def test_docs_index_redirects_to_start_wizard():
    index = read("docs/index.html")

    assert "CLEVER 시작 도우미" in index
    assert "url=start/" in index
    assert 'href="start/"' in index


def test_start_wizard_puts_work_content_before_execution_details():
    html = read("docs/start/index.html")

    assert "CLEVER 시작 도우미" in html
    assert "짧게 입력하면 에이전트용 작업 프롬프트를 생성합니다." in html
    assert "작업 경로 입력은 제거했습니다. 실행 환경별 시작 방식만 안내합니다." in html

    assert h2_texts(html) == [
        "1. 작업 요약",
        "2. 작업 분류",
        "3. 대상과 현재 상태",
        "4. 제약사항",
        "5. 실행 환경",
        "6. 생성 프롬프트",
    ]
    assert html.index("1. 작업 요약") < html.index("5. 실행 환경")
    assert html.index("하려는 일") < html.index("사용 환경")


def test_start_wizard_uses_short_chip_labels_for_classification():
    html = read("docs/start/index.html")

    for work_nature in ["신규", "기존 수정", "버그", "리팩터링", "문서/운영", "아직 모름"]:
        assert f'data-field="workNature" data-value="{work_nature}"' in html

    for target_scope in ["앱/서비스", "화면/UI", "API", "DB/model", "CI/CD", "문서", "아직 모름"]:
        assert f'data-field="targetScope" data-value="{target_scope}"' in html

    for goal_level in ["정리", "설계", "계획", "코드 변경", "테스트", "1차 MVP 개발/배포", "운영 반영", "아직 모름"]:
        assert f'data-field="goalLevel" data-value="{goal_level}"' in html

    for removed_long_label in [
        "신규 개발",
        "기존 기능 확장/수정",
        "버그 수정",
        "리팩터링/구조 개선",
        "문서/설정/운영 정리",
        "새 앱/서비스/기능",
        "CI/CD 또는 배포 workflow",
        "요구사항 정리",
        "설계 문서 작성",
        "구현 계획 수립",
        "실제 코드 변경",
        "테스트/검증",
    ]:
        assert removed_long_label not in html


def test_start_wizard_combines_target_info_and_current_state_without_detailed_fields():
    html = read("docs/start/index.html")

    assert 'id="targetInfo" data-field="targetInfo"' in html
    assert 'id="currentState" data-field="currentState"' in html
    assert "서비스/화면/API/repo/Figma/회의 메모/로그를 자유롭게 입력" in html
    assert "이미 된 것, 막힌 것, 참고할 것" in html
    assert 'id="serviceAlias"' not in html
    assert "서비스 이름(가칭)" not in html

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


def test_start_wizard_omits_workspace_picker_and_uses_current_directory_rules():
    html = read("docs/start/index.html")

    assert 'id="chooseWorkspaceButton"' not in html
    assert 'id="workspacePickerStatus"' not in html
    assert 'id="workspaceFolderInput"' not in html
    assert 'data-field="workspace"' not in html
    assert "폴더명 힌트 가져오기" not in html
    assert "workspaceFolderInput.click()" not in html
    assert "webkitRelativePath" not in html
    assert "selectedFolderNameFromFiles" not in html
    assert "pwd" in html
    assert "ls" in html
    assert 'basename "$PWD"' in html
    assert 'cd ..' in html
    assert "surfaceGuide" in html
    assert "작업 디렉터리는 에이전트가 먼저 질문하게 됩니다." in html
    assert "VS Code에서 '폴더 열기'로 작업할 폴더를 먼저 여세요." in html
    assert "원하는 작업 경로에서 터미널을 먼저 여세요." in html
    assert "window.showDirectoryPicker" not in html
    assert "workspaceDirectoryHandle" not in html
    assert "AbortError" not in html


def test_start_wizard_output_is_concise_clone_ready_and_rule_based():
    html = read("docs/start/index.html")

    for section in ["[작업]", "[대상 정보]", "[현재 상태]", "[제약사항]", "[실행 환경]", "[진행 규칙]"]:
        assert section in html

    for command in [
        "gh auth status",
        "gh api user --jq .login",
        "test -d clever-agent-project || git clone https://github.com/EVNSolution/clever-agent-project.git",
        "test -d clever-context-monorepo || git clone https://github.com/EVNSolution/clever-context-monorepo.git",
        "test -d clever-change-control || git clone https://github.com/EVNSolution/clever-change-control.git",
        'python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json',
    ]:
        assert command in html

    assert "mkdir -p clever-agent-workspace" not in html
    assert "[에이전트 작업 시작 규칙]" in html
    assert "작업 시작 전에 현재 위치를 확인하세요." in html
    assert "현재 위치가 clever-agent-project 내부라면 상위 workspace 기준으로 이동해 판단하세요." in html
    assert "현재 위치가 workspace root라면 그 위치에서 3개 repo 존재 여부를 확인하세요." in html
    assert "3개 repo가 없으면 없는 repo만 clone하세요." in html
    assert "계정이 정상 확인되면 별도로 login을 묻지 마세요." in html
    assert "recovery_actions와 next_questions만 처리하세요." in html
    assert "startup branch state로 정규화하고 진행하세요." in html
    assert "파일 수정/생성/git 작업 전에 사용자에게 한 번만 확인 질문을 하세요." in html
    assert "1. 작업 성격은 어디에 가깝나요?" not in html
    assert "먼저 하려는 일을 한 줄로 적어 주세요." not in html
    assert "navigator.clipboard.writeText" in html
    assert "copyOutput" in html


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
