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


def test_parse_issue_markdown_accepts_new_group_and_detail_fields(tmp_path: Path):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type_group: MSA/SaaS
work_type_detail: 복제
title: 배차 서비스 고객사 배포 분기 추가
---
## Work Type
- Group: MSA/SaaS
- Detail: 복제

## Purpose
내용
""",
    )

    draft = module.parse_issue_markdown(issue_md)

    assert draft.repo == "EVNSolution/clever-change-control"
    assert draft.issue_number == "3"
    assert draft.work_type_group == "MSA/SaaS"
    assert draft.work_type_detail == "복제"
    assert draft.title == "배차 서비스 고객사 배포 분기 추가"
    assert draft.formatted_title == "[MSA/SaaS][복제] 배차 서비스 고객사 배포 분기 추가"
    assert draft.body.startswith("## Work Type")


def test_parse_issue_markdown_accepts_legacy_work_type_with_compatibility_mapping(
    tmp_path: Path,
):
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

    assert draft.work_type_group == "일반 개발"
    assert draft.work_type_detail == "신규 개발"
    assert draft.formatted_title == "[일반 개발][신규 개발] 사내 문서 검색 MVP 시작"


def test_parse_issue_markdown_rejects_invalid_group_detail_combination(tmp_path: Path):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type_group: MSA/SaaS
work_type_detail: 신규 개발
title: 잘못된 조합
---
## Body
테스트
""",
    )

    with pytest.raises(ValueError) as exc:
        module.parse_issue_markdown(issue_md)

    assert "work_type_detail" in str(exc.value)


def test_parse_issue_markdown_requires_new_fields_when_legacy_work_type_missing(
    tmp_path: Path,
):
    module = load_module()
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
title: 제목만 있음
---
본문
""",
    )

    with pytest.raises(ValueError) as exc:
        module.parse_issue_markdown(issue_md)

    message = str(exc.value)
    assert "work_type_group" in message
    assert "work_type_detail" in message


def test_cli_dry_run_prints_bracketed_taxonomy_title(tmp_path: Path):
    issue_md = write_issue_md(
        tmp_path,
        """---
repo: EVNSolution/clever-change-control
issue_number: 3
work_type_group: 일반 개발
work_type_detail: 수정
title: 제목 규칙 변경
---
## Work Type
- Group: 일반 개발
- Detail: 수정

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
    assert payload["title"] == "[일반 개발][수정] 제목 규칙 변경"
    assert payload["dry_run"] is True
    assert payload["updated"] is False


def test_formatted_title_truncates_overlong_titles():
    module = load_module()
    draft = module.IssueDraft(
        repo="EVNSolution/clever-change-control",
        issue_number="3",
        work_type_group="일반 개발",
        work_type_detail="리팩토링",
        title="bootstrap helper 구조를 단순화하고 worktree 해석 흐름을 더 읽기 쉽게 정리한다",
        body="## Body\n내용",
    )

    assert (
        draft.formatted_title
        == "[일반 개발][리팩토링] bootstrap helper 구조를 단순화하고 worktree 해석 흐름을..."
    )
