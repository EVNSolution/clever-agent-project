---
name: bootstrap-clever-work
description: Use when starting work from any CLEVER repo and the intake must be standardized against clever-context-monorepo and clever-change-control before planning or implementation begins
---

# Bootstrap CLEVER Work

## Overview

Use this skill as the single entry point for new CLEVER work.

It forces the same start sequence for every user and every repo:

1. Read the two SSOT repos first.
2. Infer the work context from the current repo.
3. Convert the request into a `project-start` draft packet.
4. Ask for one final approval.
5. Only then create the root issue, propose repo bootstrap, clone the repo, and hand off.

**Core principle:** do not start CLEVER work from a freeform prompt when the SSOT repos are available.

The canonical identifier is the created `project-start` issue number in `clever-change-control`. Before issue creation, the workflow uses a `project-start` draft only.

## SSOT Order

Interpret sources in this order:

1. `clever-context-monorepo`
2. `clever-change-control`
3. the current working repo

The current repo is the execution surface, not the source of truth for workflow rules.

## When to Use

Use this skill when:

- work starts from any CLEVER repo and the intake needs to be standardized
- the user gives a goal but not all of `target repo` or implementation details
- different people or agents need to start work in the same format
- you need to prepare the root `project-start` record before planning

Do not use this skill when:

- the work is not inside the CLEVER workspace
- a `project-start` draft or issue has already been approved for the current task

## Required Inputs

The user only needs to provide the business intent.

You should infer or propose the rest:

- `user-session`
- `current-working-repo`
- `target-repo`
- `purpose`
- `constraints`
- `ui-impact`
- `expected-result`

The workflow must not require a pre-confirmed `target-service` or a generated `change-id` at start time.

## First Step

Run the helper script from this repository-local skill.

```bash
python3 scripts/bootstrap_clever_work.py --cwd "$PWD"
```

If the user already provided fields such as purpose or constraints, pass them through:

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --purpose "<purpose>" \
  --constraints "<constraints>" \
  --ui-impact "<있음|없음|unknown>" \
  --expected-result "<expected result>" \
  --target-repo "<target repo if known>"
```

The `scripts/` path is relative to this skill directory inside `clever_agent_project/.codex/skills/bootstrap-clever-work/`.

The script emits:

- the standardized bootstrap packet
- the SSOT docs it used
- a `project_start_issue` draft
- a `repo_bootstrap` proposal
- a `repo_session_handoff` recommendation

## Approval Gate

After the script runs, present the packet in the conversation and ask exactly one approval question:

> "아래 project-start 초안과 repo bootstrap 제안으로 진행할까요? 틀리면 수정할 필드만 말해 주세요."

Do not create or update records before this approval.

## After Approval

Once the user approves:

1. Treat the packet as locked context for the rest of the task.
2. Create the `project-start` issue in `clever-change-control`.
3. Use the created issue number as the canonical identifier.
4. Propose creation or confirmation of the target repo after the issue exists.
5. Clone or pull the target repo locally.
6. Recommend a new session in the cloned target repo for planning or implementation.

Do not create service-doc drafts in the normal start path.

## Standard Packet

Every run should normalize the start state into this shape:

```text
user-session:
current-working-repo:
current-working-repo-path:
target-repo:
purpose:
constraints:
ui-impact:
expected-result:
ssot-docs-read:
project-start-issue:
repo-bootstrap:
repo-session-handoff:
next-step:
```

Never replace this with a looser narrative summary.

## Common Mistakes

- Treating the current repo as the workflow SSOT.
- Starting implementation before the `project-start` issue is drafted and approved.
- Requiring an inferred `target-service` before the intake can begin.
- Generating a canonical `change-id` before the root issue exists.
- Creating service-doc work in the normal bootstrap path.
- Editing change-control or repo resources before the final approval step.

## Real-World Impact

This skill exists to reduce user effort without reducing control:

- non-developers can give business intent instead of process details
- agents start from the same intake structure every time
- root issue creation, repo bootstrap, and session handoff stay aligned from the beginning
