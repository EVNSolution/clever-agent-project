#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FIELDS = ("repo", "issue_number", "title")
LEGACY_WORK_TYPE_MAP = {
    "신규 개발": ("일반 개발", "신규 개발"),
    "신규": ("일반 개발", "신규 개발"),
    "수정": ("일반 개발", "수정"),
    "변경": ("일반 개발", "변경"),
    "리팩토링": ("일반 개발", "리팩토링"),
}
WORK_TYPE_GROUPS = {
    "MSA/SaaS": ("복제", "수정", "변경", "신규"),
    "일반 개발": ("신규 개발", "수정", "변경", "리팩토링"),
}
TITLE_BODY_MAX_LENGTH = 45
TITLE_ENDING_PATTERNS = (
    re.compile(
        r"(?:을|를)\s*(준비|구현|개발|정리|개선|변경|수정|추가|삭제|도입|작성|구축|설계)(?:한다|합니다)$"
    ),
    re.compile(
        r"\s*(준비|구현|개발|정리|개선|변경|수정|추가|삭제|도입|작성|구축|설계)(?:한다|합니다)$"
    ),
)


def normalize_field(value: str) -> str:
    return " ".join(value.split())


def normalize_title_body(title: str) -> str:
    normalized = normalize_field(title).rstrip(".!? ")

    for pattern in TITLE_ENDING_PATTERNS:
        candidate = pattern.sub("", normalized).rstrip()
        if candidate and candidate != normalized:
            normalized = candidate
            break

    return normalized or "제목 미정"


def truncate_title_body(title: str, *, max_length: int = TITLE_BODY_MAX_LENGTH) -> str:
    if len(title) <= max_length:
        return title
    if max_length <= 3:
        return "." * max_length
    return title[: max_length - 3].rstrip() + "..."


def validate_group_and_detail(group: str, detail: str) -> tuple[str, str]:
    normalized_group = normalize_field(group)
    normalized_detail = normalize_field(detail)

    if normalized_group not in WORK_TYPE_GROUPS:
        allowed_groups = ", ".join(WORK_TYPE_GROUPS)
        raise ValueError(
            f"Invalid work_type_group: {normalized_group!r}. Allowed values: {allowed_groups}"
        )

    if normalized_detail not in WORK_TYPE_GROUPS[normalized_group]:
        allowed_details = ", ".join(WORK_TYPE_GROUPS[normalized_group])
        raise ValueError(
            "Invalid work_type_detail for work_type_group: "
            f"work_type_group={normalized_group!r}, "
            f"work_type_detail={normalized_detail!r}, "
            f"allowed values: {allowed_details}"
        )

    return normalized_group, normalized_detail


def resolve_work_type(metadata: dict[str, str]) -> tuple[str, str]:
    group = metadata.get("work_type_group")
    detail = metadata.get("work_type_detail")
    legacy = metadata.get("work_type")

    if group or detail:
        missing = [
            field
            for field, value in (
                ("work_type_group", group),
                ("work_type_detail", detail),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing required front matter field(s): " + ", ".join(missing)
            )
        return validate_group_and_detail(group or "", detail or "")

    if legacy:
        normalized_legacy = normalize_field(legacy)
        mapped = LEGACY_WORK_TYPE_MAP.get(normalized_legacy)
        if mapped is None:
            allowed_legacy = ", ".join(LEGACY_WORK_TYPE_MAP)
            raise ValueError(
                f"Invalid work_type: {normalized_legacy!r}. Allowed values: {allowed_legacy}"
            )
        return mapped

    raise ValueError(
        "Missing required front matter field(s): work_type_group, work_type_detail"
    )


@dataclass(frozen=True)
class IssueDraft:
    repo: str
    issue_number: str
    work_type_group: str
    work_type_detail: str
    title: str
    body: str

    @property
    def formatted_title(self) -> str:
        title = truncate_title_body(normalize_title_body(self.title))
        return f"[{self.work_type_group}][{self.work_type_detail}] {title}"


def parse_issue_markdown(path: Path) -> IssueDraft:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError("Markdown front matter must start with '---'.")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("Markdown front matter closing '---' is missing.")

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid front matter line: {line!r}")
        metadata[key.strip()] = value.strip()

    missing = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        raise ValueError(
            "Missing required front matter field(s): " + ", ".join(missing)
        )

    work_type_group, work_type_detail = resolve_work_type(metadata)

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n").rstrip()
    if not body:
        raise ValueError("Issue body is empty. Add markdown content below front matter.")

    return IssueDraft(
        repo=metadata["repo"],
        issue_number=metadata["issue_number"],
        work_type_group=work_type_group,
        work_type_detail=work_type_detail,
        title=metadata["title"],
        body=body,
    )


def update_issue_with_gh(draft: IssueDraft) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".md", delete=False
    ) as temp_file:
        temp_file.write(draft.body)
        temp_path = Path(temp_file.name)

    try:
        return subprocess.run(
            [
                "gh",
                "issue",
                "edit",
                draft.issue_number,
                "-R",
                draft.repo,
                "--title",
                draft.formatted_title,
                "--body-file",
                str(temp_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sync a GitHub issue title/body from markdown front matter. "
            "Title format is '[work_type_group][work_type_detail] <short_title>'."
        )
    )
    parser.add_argument("markdown_file", help="Path to markdown file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed values without editing the GitHub issue",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markdown_path = Path(args.markdown_file).resolve()

    try:
        draft = parse_issue_markdown(markdown_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    payload: dict[str, object] = {
        "repo": draft.repo,
        "issue_number": draft.issue_number,
        "title": draft.formatted_title,
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        payload["updated"] = False
    else:
        try:
            proc = update_issue_with_gh(draft)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            if stderr:
                print(stderr, file=sys.stderr)
            return exc.returncode or 1
        payload["updated"] = True
        payload["url"] = (proc.stdout or "").strip()

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
