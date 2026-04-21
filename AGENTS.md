# AGENTS.md

## Scope

This file defines the startup contract for agents working from `clever-agent-project`.

This repository is **not** a standalone execution environment.
It is the entrypoint of a **local three-repository control-plane workspace**.

## Workspace Contract

Before doing any real work, confirm that all of the following repositories exist in the same local workspace root:

1. `clever-agent-project`
2. `clever-context-monorepo`
3. `clever-change-control`

If any of these repositories are missing, the workspace is incomplete.
Do not pretend web links are a substitute for local context.
Stop and state that the three-repository local workspace is required.

## What Each Repository Owns

- `clever-agent-project`
  - Entry point
  - Intake
  - Bootstrap packet generation
  - Handoff into target repositories

- `clever-context-monorepo`
  - Canonical interpretation
  - Template lineage
  - Service metadata
  - Deploy baseline

- `clever-change-control`
  - `project-start` root
  - Scoped change requests
  - Rollout / rollback trace
  - Release evidence linkage

Actual implementation work happens in a separate **target repository**.
The three repositories above form the control plane, not the product implementation plane.

## Document Roles Inside This Repository

Treat the main documents in `clever-agent-project` as separate layers:

- `README.md`
  - Human-facing portal
  - Workspace-first summary
  - Quick navigation into the control plane

- `docs/setting.md`
  - Operational manual
  - Runtime prerequisites
  - Workspace topology
  - Bootstrap expectations
  - Startup rules and local operating assumptions

- `docs/guides/clever-project-workflows.md`
  - Scenario guide
  - New build vs. maintenance vs. handoff flow

- `.agent/skills/bootstrap-clever-work/SKILL.md`
  - Agent execution rulebook
  - Startup hard gate
  - Bootstrap behavior

Do not collapse these roles into one document in your own reasoning.
Read `docs/setting.md` as the detailed operating reference for this repository.

## Startup Read Order

When starting work from this repository, read in this order:

1. `README.md`
2. `docs/setting.md`
3. `docs/guides/clever-project-workflows.md`
4. `.agent/skills/bootstrap-clever-work/SKILL.md`
5. `../clever-context-monorepo/docs/root/authority-boundaries.md`
6. `../clever-context-monorepo/docs/root/index.md`
7. `../clever-change-control/README.md`

If the task is service-specific, also read:

- `../clever-context-monorepo/docs/services/<service>/index.md`

If the task is template-specific, also read:

- `../clever-context-monorepo/docs/templates/index.md`

## First-Response Contract

Do not jump straight into implementation.

For a new session, begin by collecting the startup frame:

1. New service development vs. existing service extension
2. Service base: MSA vs. MONO
3. Explicit work type classification

Also collect:

- what the user wants to do
- why it is needed
- constraints
- expected result
- related repo or service, if already known

If the user starts in free-form text, normalize their request into this structure before proceeding.

## Authority Rules

These rules are mandatory:

- The canonical root start record is `project-start issue #`
- `change_id` is **not** the root start identifier
- `change_id` only becomes required after scoped execution is fixed
- Do not require a fixed `target_service` at generic intake start
- Do not assume the implementation repository is already known at session open

Short version:

- start in `clever-agent-project`
- interpret in `clever-context-monorepo`
- anchor and trace in `clever-change-control`
- implement in the target repository

## What Not To Do

Do not:

- treat this repository as the only source of truth
- treat GitHub links as sufficient when local repositories are missing
- open scoped execution before the root line is understood
- force `change_id` too early
- force a concrete `target_service` too early
- implement product code in control-plane repositories unless the task is explicitly about the control plane

## Expected Flow

The expected operating flow is:

1. Verify the three-repository local workspace
2. Gather the startup frame
3. Read canonical context
4. Draft the `project-start` payload
5. Anchor the root line in `clever-change-control`
6. Fix scoped execution
7. Handoff to the target repository
8. Feed rollout / rollback / release evidence back into `clever-change-control`

## If The Workspace Is Incomplete

Say this clearly:

> CLEVER requires a local three-repository workspace:
> `clever-agent-project`, `clever-context-monorepo`, and `clever-change-control`.
> This workspace is incomplete, so startup interpretation and traceability are degraded.

Do not continue as if the environment were complete.
