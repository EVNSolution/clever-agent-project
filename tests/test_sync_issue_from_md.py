from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts/sync_issue_from_md.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_issue_from_md", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_issue_md(tmp_path: Path, content: str) -> Path:
    issue_md = tmp_path / "issue.md"
    issue_md.write_text(content, encoding="utf-8")
    return issue_md


def test_parse_issue_markdown_extracts_metadata_and_body(tmp_path: Path):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type: 신규 개발
title: 사내 문서 검색 MVP 시작
---
## Purpose
내용
""",
    )

    draft = module.parse_issue_markdown(issue_md)

    assert draft.repo == "EVNSolution/clever-change-control"
    assert draft.issue_number == "3"
    assert draft.work_type == "신규 개발"
    assert draft.title == "사내 문서 검색 MVP 시작"
    assert draft.formatted_title == "신규/사내 문서 검색 MVP 시작"
    assert draft.body.startswith("## Purpose")


def test_parse_issue_markdown_requires_required_fields(tmp_path: Path):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
title: 제목만 있음
---
본문
""",
    )

    with pytest.raises(ValueError) as exc:
        module.parse_issue_markdown(issue_md)

    message = str(exc.value)
    assert "issue_number" in message
    assert "work_type" in message


def test_cli_dry_run_prints_computed_values(tmp_path: Path):
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type: 수정
title: 제목 규칙 변경
---
## Body
테스트
""",
    )

    proc = subprocess.run(
        ["python3", str(MODULE_PATH), str(issue_md), "--dry-run"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)

    assert payload["repo"] == "EVNSolution/clever-change-control"
    assert payload["issue_number"] == "3"
    assert payload["title"] == "수정/제목 규칙 변경"
    assert payload["dry_run"] is True
    assert payload["updated"] is False


def test_formatted_title_shortens_work_type_and_removes_trailing_action_phrase(tmp_path: Path):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type: 신규 개발
title: 사내 문서 검색과 요약을 제공하는 AI 헬프데스크 웹앱 MVP를 준비한다.
---
## Purpose
내용
""",
    )

    draft = module.parse_issue_markdown(issue_md)

    assert draft.formatted_title == "신규/사내 문서 검색과 요약을 제공하는 AI 헬프데스크 웹앱 MVP"


def test_formatted_title_truncates_overlong_titles():
    module = load_module()
    draft = module.IssueDraft(
        repo="EVNSolution/clever-change-control",
        issue_number="3",
        work_type="리팩토링",
        title="bootstrap helper 구조를 단순화하고 worktree 해석 흐름을 더 읽기 쉽게 정리한다",
        body="## Body\n내용",
    )

    assert draft.formatted_title == "리팩토링/bootstrap helper 구조를 단순화하고 worktree 해석 흐름을..."
