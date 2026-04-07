# clever_agent_project

Project-local agent assets for the CLEVER workspace.

## Purpose

This repository stores CLEVER-specific agent skills and supporting files without relying on a global superpowers installation.

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
- The skill is repository-local on purpose. It is not meant to live in `/Users/jiin/superpowers/skills`.
