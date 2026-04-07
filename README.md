# clever_agent_project

Project-local agent assets for the CLEVER workspace.

## Purpose

This repository stores CLEVER-specific agent skills and supporting files without relying on a global superpowers installation.

## Execution Guide

Use this repository as the intake surface for any new CLEVER work.

### Preconditions

Keep the CLEVER repos in one workspace root.

```text
<CLEVER_ROOT>/
  clever_agent_project/
  clever-change-control/
  clever-context-monorepo/
```

Start the session in `<CLEVER_ROOT>/clever_agent_project`.

### Required Read Order

Before drafting anything, read in this order:

1. read this README
2. read `.codex/skills/bootstrap-clever-work/SKILL.md`
3. read the current SSOT state in `clever-change-control` and `clever-context-monorepo`

Do not start planning or implementation before that read order is complete.

### Step 1: Build the Bootstrap Packet

Run the repo-local helper from `clever_agent_project`:

```bash
python3 .codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py --cwd "$PWD" --json
```

If the user already gave purpose, constraints, expected result, or a known target repo, pass them through:

```bash
python3 .codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --purpose "<purpose>" \
  --constraints "<constraints>" \
  --expected-result "<expected result>" \
  --target-repo "<target repo if known>" \
  --json
```

Expected result:

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`
- `ssot_docs_read`

### Step 2: Present the Approval Gate

Show the packet summary to the user and ask exactly one approval question:

> 아래 project-start 초안과 repo bootstrap 제안으로 진행할까요? 틀리면 수정할 필드만 말해 주세요.

Do not create a GitHub issue, repo, branch, folder, or SSOT change before approval.

### Step 3: After Approval

After approval, the execution order is:

1. create the `project-start` issue in `clever-change-control`
2. use the created `project-start issue #` as the canonical identifier
3. propose or confirm the target repo
4. create the target GitHub repo if needed
5. clone or pull the target repo locally
6. hand off to a fresh session rooted in the target repo

### Step 4: Handoff Rule

The default next session is a new session in the target repo.

Keep `clever_agent_project` as the intake and orchestration surface. Do not treat it as the default execution repo unless the approved packet explicitly says so.

### Do Not

- do not generate a canonical `change_id`
- do not require `target_service` before the start draft exists
- do not create service-doc drafts in the normal start path
- do not modify SSOT source during ordinary project intake
- do not skip the approval gate

## Current Asset

- `.codex/skills/bootstrap-clever-work/`

`bootstrap-clever-work` standardizes new work intake by treating:

- `clever-context-monorepo` as the context and workflow SSOT
- `clever-change-control` as the change-record SSOT

The skill now starts from a `project-start` draft instead of a generated `change_id` or inferred `target_service`.

Its normal flow is:

1. draft a `project-start` issue for `clever-change-control`
2. ask for approval
3. create the issue
4. propose target repo bootstrap
5. clone or pull the target repo locally
6. recommend a fresh session in the target repo

The resulting canonical identifier is the created `project-start` issue number. Before issue creation, the helper emits a repo-local draft packet with:

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`

The normal start path does not generate a canonical `change_id` and does not prepare service-doc creation work.

## Repository Layout

```text
.codex/
  skills/
    bootstrap-clever-work/
      SKILL.md
      agents/openai.yaml
      scripts/bootstrap_clever_work.py
```

## Notes

- This repository is intended to be versioned and shared with CLEVER contributors.
- The skill is repository-local on purpose. It is not meant to live in a user-specific global skills directory.
