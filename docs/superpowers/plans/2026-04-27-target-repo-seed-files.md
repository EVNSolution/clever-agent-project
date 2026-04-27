# Target Repo Seed Files Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make CLEVER bootstrap packets tell agents to seed each new target repo with an execution-focused `AGENTS.md` and a separate project brief draft.

**Architecture:** Keep seed-file templates in `clever-agent-project/docs/templates/` because the start repo owns bootstrap handoff behavior. The helper script should expose the template source paths, destination paths, purpose, and required placeholders in `target_repo_seed_files` so repo creation can copy the right files without mixing execution rules with project planning.

**Tech Stack:** Python bootstrap helper, Markdown templates, pytest

---

### Task 1: Bootstrap Packet Seed Files

**Files:**
- Modify: `.agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py`
- Modify: `.gitignore`
- Create: `docs/templates/target-repo-AGENTS.md`
- Create: `docs/templates/target-repo-project-brief.md`
- Modify: `docs/setting.md`
- Modify: `docs/guides/clever-project-workflows.md`
- Modify: `tests/test_bootstrap_clever_work.py`

- [x] **Step 1: Write the failing test**

Add assertions that `build_packet()` returns `target_repo_seed_files` with:

```python
seed_files = packet["target_repo_seed_files"]
assert seed_files[0]["destination"] == "AGENTS.md"
assert seed_files[0]["role"] == "agent execution procedure"
assert seed_files[1]["destination"] == "docs/project-brief.md"
assert seed_files[1]["role"] == "project planning draft"
assert "copy these files into the target repo before handoff" in packet["repo_bootstrap"]["post_create_clone"]
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_bootstrap_clever_work.py -k seed_files -v`

Expected: FAIL because `target_repo_seed_files` does not exist yet.

- [x] **Step 3: Add minimal implementation**

Add a helper that returns two seed-file records:

```python
def build_target_repo_seed_files() -> list[dict[str, Any]]:
    return [
        {
            "source_template": "clever-agent-project/docs/templates/target-repo-AGENTS.md",
            "destination": "AGENTS.md",
            "role": "agent execution procedure",
            "purpose": "Define the order, method, checklists, and completion rules agents must follow in the target repo.",
        },
        {
            "source_template": "clever-agent-project/docs/templates/target-repo-project-brief.md",
            "destination": "docs/project-brief.md",
            "role": "project planning draft",
            "purpose": "Capture the initial project intent, constraints, scope, and unresolved planning questions.",
        },
    ]
```

- [x] **Step 4: Add template files and documentation links**

Create the two Markdown templates and link them from the operations docs.

- [x] **Step 5: Run verification**

Run:

```bash
python3 -m pytest tests
git diff --check
```

Expected: all tests pass and no whitespace errors.
