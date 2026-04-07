# clever_agent_project

Project-local agent assets for the CLEVER workspace.

## Purpose

This repository stores CLEVER-specific agent skills and supporting files without relying on a global superpowers installation.

## Start Here

Use this repository as the intake surface for any new CLEVER work.

Recommended local layout:

```text
<CLEVER_ROOT>/
  clever_agent_project/
  clever-change-control/
  clever-context-monorepo/
```

When a new session agent starts here, it should:

1. read this README
2. read `.codex/skills/bootstrap-clever-work/SKILL.md`
3. read the current SSOT state in `clever-change-control` and `clever-context-monorepo`
4. draft a `project-start` issue
5. wait for approval
6. create the issue, bootstrap the target repo, and hand off to a fresh target-repo session

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
