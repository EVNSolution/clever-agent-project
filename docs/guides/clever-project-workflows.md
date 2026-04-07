# CLEVER Project Workflows

This document explains how CLEVER work should start and how to decide between:

- starting a brand-new project
- improving an existing repo
- re-implementing an existing repo or service

## Core Rule

The real start of work is not repo creation.

The real start of work is creating a `project-start` issue in `clever-change-control`.

That issue number becomes the canonical identifier for the whole line of work.

## Repositories and Roles

- `clever_agent_project`: intake and orchestration surface
- `clever-change-control`: root issue, child issue, approval, and traceability surface
- `clever-context-monorepo`: SSOT for rules, terminology, and documentation boundaries

## Always-True Rules

These rules apply in every case:

1. Start in `clever_agent_project`.
2. Read SSOT before drafting work.
3. Create a `project-start` draft before creating or changing repos.
4. Wait for approval before creating the GitHub issue or bootstrapping repos.
5. Use the created `project-start issue #` as the canonical identifier.
6. Treat `target_service` as optional at start.
7. Do not generate a canonical `change_id`.

## Flow 1: Start a Brand-New Project

Use this flow when the work does not already belong under an existing `project-start`.

Typical signals:

- the work is a new initiative
- the first concrete decision may be to create one or more repos
- the project boundary, repo layout, or service split is still open

Execution flow:

1. Start in `clever_agent_project`.
2. Read `clever-context-monorepo` and `clever-change-control`.
3. Draft a `project-start`.
4. Get approval.
5. Create the `project-start` issue.
6. Use the created issue number as the root identifier.
7. Decide the first target repo.
8. Create the GitHub repo if needed.
9. Clone or pull it locally.
10. Move to a new session in that target repo.

Result:

- one root `project-start`
- zero or more repos created under that root
- later child issues attached to the same root

## Flow 2: Improve an Existing Repo

Use this flow when the work clearly belongs to an already running project line.

Typical signals:

- the repo already exists
- the initiative already has a valid `project-start`
- the work is another feature, fix, or scoped change inside that line

Execution flow:

1. Identify the existing parent `project-start #`.
2. Do not create a new root issue unless the initiative boundary changed.
3. Create the appropriate child issue:
   - `new`
   - `fix`
   - `change`
   - `refactoring`
4. Reference the parent `project-start #`.
5. Confirm or refresh the local checkout of the existing target repo.
6. Continue implementation in the repo session.

Result:

- same root `project-start`
- new child issue under that root
- no new repo unless the approved change explicitly requires one

## Flow 3: Re-Implement an Existing Repo or Service

Re-implementation can go in two different directions.

### Case A: Large internal rewrite inside the same initiative

Use the existing `project-start` when:

- the product line is the same
- the business initiative is the same
- the work is still traceable as a continuation of the current project

In this case, create a child issue, usually `refactoring` or sometimes `change`.

### Case B: New initiative using an existing repo or service

Create a new `project-start` when:

- the project is being repositioned or restarted
- the scope is large enough that you want a new root traceability line
- the business goal is materially different from the old one
- you want approvals, bootstrap decisions, and follow-on issues separated from the previous line

In this case, the repo may stay the same, but the root issue is new.

That means:

- same repo is possible
- same service is possible
- same codebase is possible
- but the root governance line becomes a new `project-start`

## How to Decide: New `project-start` or Existing One?

Ask one question:

Does this work belong to the same initiative boundary, or does it need a new root traceability line?

If it is the same initiative boundary:

- keep the existing `project-start`
- create a child issue

If it needs a new root traceability line:

- create a new `project-start`
- even if the repo is already there

## What the User Usually Needs to Provide

At start, the user should usually provide only:

- one or two sentences of purpose or background
- any important constraint if one already exists

The workflow should not force the user to decide all of these upfront:

- target repo
- target service
- repo count
- detailed implementation plan

## What Happens After Approval

After approval, the agent may:

1. create the `project-start` issue
2. use its issue number as the canonical identifier
3. create or confirm the target repo
4. clone or pull the repo locally
5. hand off to a fresh session in the target repo

## What Normal Projects Must Not Do

During ordinary project execution:

- do not treat SSOT repos as normal implementation targets
- do not modify SSOT source casually
- do not restore `change_id` as the root identifier
- do not require `target_service` before drafting the root issue

## Short Version

- New initiative: create a new `project-start`.
- Existing initiative, existing repo work: create a child issue under the existing `project-start`.
- Existing repo but new initiative: create a new `project-start`, even if the repo stays the same.
