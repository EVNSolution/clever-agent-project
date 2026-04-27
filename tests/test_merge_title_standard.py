from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_ROOT = REPO_ROOT.parent / "clever-context-monorepo"
CHANGE_CONTROL_ROOT = REPO_ROOT.parent / "clever-change-control"

DEFAULT_MERGE_SUBJECT = "Merge pull request #<pr-number> from <owner>/<source-branch>"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_merge_title_standard_uses_github_default_prefix():
    docs = [
        read(REPO_ROOT / "AGENTS.md"),
        read(REPO_ROOT / "README.md"),
        read(CONTEXT_ROOT / "AGENTS.md"),
        read(CONTEXT_ROOT / "README.md"),
        read(CONTEXT_ROOT / "docs/root/pipeline-governance.md"),
        read(CHANGE_CONTROL_ROOT / "AGENTS.md"),
        read(CHANGE_CONTROL_ROOT / "README.md"),
        read(REPO_ROOT / "docs/templates/target-repo-AGENTS.md"),
    ]

    for text in docs:
        assert "PR-MERGE" not in text
        assert DEFAULT_MERGE_SUBJECT in text
