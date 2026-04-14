# Template Harness And Deploy Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a versioned template harness and deploy baseline so CLEVER agents always ask users to choose a template, record the choice as service lineage, and reuse that lineage for future maintenance.

**Architecture:** Keep `clever-context-monorepo` as the source of truth for template registry, deploy baseline, and service lineage metadata. Keep `clever-agent-project` as the intake surface that always presents template options and emits the chosen template/deploy metadata in the bootstrap packet. Keep `clever-change-control` as the tracking surface that mirrors the selected template metadata in issue guidance and issue body structure.

**Tech Stack:** Markdown documentation, repo-local skill docs, Python 3, pytest, git, GitHub issue form YAML

---

## File Map

### `clever-context-monorepo`

- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/template-harness-governance.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/deploy-template-governance.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/index.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/index.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/versions/v1.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/README.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/checklist.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/env-template.example`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/override-guide.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/services.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/service-template.md`

### `clever-agent-project`

- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/templates/issue-edit-template.md`
- Test: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_bootstrap_clever_work.py`

### `clever-change-control`

- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`

### Design Choice Locked By This Plan

- Service lineage metadata will be added as an explicit Markdown section in `docs/services/service-template.md`, not YAML front matter.
- The bootstrap helper will support explicit template fields and will emit `needs-selection` placeholders when the user has not chosen a template yet.
- `TEST-Erik-project-template` will be registered as an upstream template entry, not copied into CLEVER as a scaffold codebase.

### Task 1: Author template registry and deploy baseline docs in `clever-context-monorepo`

**Files:**
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/template-harness-governance.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/deploy-template-governance.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/index.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/index.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/templates/test-erik-project-template/versions/v1.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/root/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/index.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/wiki/services.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/index.md`

- [ ] **Step 1: Write `template-harness-governance.md`**

Document these exact rules:
- template choices are always shown to the user
- maintenance defaults to the service's recorded template lineage
- switching templates is a `migration`, not a normal edit
- unregistered templates are allowed but must be recorded as candidates
- template states are `recommended`, `legacy`, `deprecated`

- [ ] **Step 2: Write `deploy-template-governance.md`**

Document the shared deploy baseline using the existing central deploy truth:
- image build source vs central deploy destination
- env/secret separation
- rollout/rollback checklist expectations
- public contract probe after deploy
- customer-specific override boundaries

- [ ] **Step 3: Write the template registry entry point**

In `docs/templates/index.md`, define the catalog format and list the initial registered template:
- `test-erik-project-template@v1`

Include the required fields:
- `template_id`
- `version`
- `status`
- `use_case`
- `deploy_profile`
- `summary`

- [ ] **Step 4: Write the Erik template adapter docs**

In `docs/templates/test-erik-project-template/index.md` and `versions/v1.md`, capture:
- upstream repo URL
- when it should be chosen
- when it should not be chosen
- which folders and workflows CLEVER adopts conceptually
- which deploy profile it maps to
- known constraints

- [ ] **Step 5: Link the new registry and governance docs from existing entry points**

Update:
- `docs/root/index.md`
- `docs/wiki/index.md`
- `docs/wiki/services.md`
- `docs/services/index.md`

The links must keep `docs/root` as the source of truth and `docs/wiki` as navigation only.

- [ ] **Step 6: Verify the context docs patch formatting**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo diff --check -- \
  docs/root/index.md \
  docs/root/template-harness-governance.md \
  docs/root/deploy-template-governance.md \
  docs/wiki/index.md \
  docs/wiki/services.md \
  docs/services/index.md \
  docs/templates
```

Expected: no output

- [ ] **Step 7: Commit the registry and governance docs**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo add \
  docs/root/index.md \
  docs/root/template-harness-governance.md \
  docs/root/deploy-template-governance.md \
  docs/wiki/index.md \
  docs/wiki/services.md \
  docs/services/index.md \
  docs/templates
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo commit -m "docs: add template harness governance"
```

Expected: one commit containing the new template registry and root governance docs only

### Task 2: Add deploy baseline assets and service lineage structure in `clever-context-monorepo`

**Files:**
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/README.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/checklist.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/env-template.example`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/templates/deploy/override-guide.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo/docs/services/service-template.md`

- [ ] **Step 1: Write the deploy template asset README**

Describe what `templates/deploy/` contains, what is baseline vs override, and how it relates to `docs/root/deploy-template-governance.md`.

- [ ] **Step 2: Write the deploy checklist**

Include a concise checklist for:
- image build readiness
- secret/env readiness
- central deploy trigger readiness
- post-deploy public contract verification
- rollback readiness

- [ ] **Step 3: Write the env template example and override guide**

Keep the example generic. It should demonstrate structure only, not real secrets. The override guide must explain where customer-specific values are allowed to diverge.

- [ ] **Step 4: Extend `docs/services/service-template.md`**

Add a new explicit section such as `## Template Harness / Lineage` with these fields:
- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_state`

Keep the existing service-purpose sections intact and refer global rules back to the new root docs.

- [ ] **Step 5: Verify the deploy assets and service template patch formatting**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo diff --check -- \
  templates/deploy \
  docs/services/service-template.md
```

Expected: no output

- [ ] **Step 6: Commit the deploy assets and service lineage template**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo add \
  templates/deploy \
  docs/services/service-template.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo commit -m "docs: add deploy baseline assets"
```

Expected: one commit containing only deploy template assets and the service template lineage section

### Task 3: Update `clever-agent-project` docs and draft template to require template choice

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/templates/issue-edit-template.md`

- [ ] **Step 1: Update `README.md` with the template choice policy**

Document that:
- after work-type branching, template choices are always shown to the user
- maintenance work must read service lineage from `clever-context-monorepo` first
- the previous template is the default recommendation, not an automatic lock
- the chosen template metadata must be recorded in the bootstrap packet and issue body

- [ ] **Step 2: Update `bootstrap-clever-work` skill with the same rule**

Explicitly tell agents to:
- read the template registry from `clever-context-monorepo`
- present template options every time
- prefer the existing lineage for maintenance
- treat template changes as `migration`

- [ ] **Step 3: Extend `docs/templates/issue-edit-template.md`**

Add visible fields and body placeholders for:
- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_action`

Keep the existing work-type taxonomy fields and place the template/deploy block near the top of the body.

- [ ] **Step 4: Verify doc patch formatting in `clever-agent-project`**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project diff --check -- \
  README.md \
  .agent/skills/bootstrap-clever-work/SKILL.md \
  docs/templates/issue-edit-template.md
```

Expected: no output

- [ ] **Step 5: Commit the intake doc and template changes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add \
  README.md \
  .agent/skills/bootstrap-clever-work/SKILL.md \
  docs/templates/issue-edit-template.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "docs: add template harness intake rules"
```

Expected: one commit for intake docs and draft template changes only

### Task 4: Extend the bootstrap helper and tests with template/deploy metadata

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py`
- Test: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_bootstrap_clever_work.py`

- [ ] **Step 1: Write failing tests for the new bootstrap packet shape**

Add tests that assert the packet carries:
- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_action`

Cover both cases:
- explicit values provided
- omitted values falling back to `needs-selection`

Also assert the project-start body gets a visible `Template Harness` or equivalent section.

- [ ] **Step 2: Run the targeted bootstrap tests and confirm failure**

Run:

```bash
pytest /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_bootstrap_clever_work.py -q
```

Expected: failures because the current helper does not know template/deploy metadata

- [ ] **Step 3: Extend CLI arguments and packet construction**

Update `bootstrap_clever_work.py` to accept optional flags such as:
- `--template-id`
- `--template-version`
- `--deploy-profile`
- `--override-scope`
- `--lifecycle-action`

If a flag is missing, emit `needs-selection` in the packet instead of silently choosing a template.

- [ ] **Step 4: Extend the SSOT doc list for template/deploy governance**

Make `build_ssot_docs()` include the new root/template docs that an intake agent must read before asking the template question.

- [ ] **Step 5: Extend text and JSON output**

Update `print_text_packet()` and the project-start issue body so they show the selected or pending template/deploy values in a clearly labeled section.

Concrete expected body fragment:

```text
## Template Harness
- template_id: test-erik-project-template
- template_version: v1
- deploy_profile: central-image-backed
- override_scope: customer-config-only
- lifecycle_action: adopt
```

- [ ] **Step 6: Run the targeted bootstrap tests and confirm pass**

Run:

```bash
pytest /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_bootstrap_clever_work.py -q
```

Expected: all tests pass

- [ ] **Step 7: Run the helper in JSON mode and inspect the packet**

Run:

```bash
python3 /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py \
  --cwd /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project \
  --template-id test-erik-project-template \
  --template-version v1 \
  --deploy-profile central-image-backed \
  --override-scope customer-config-only \
  --lifecycle-action adopt \
  --json
```

Expected: JSON packet includes those fields and the project-start body contains a template section

- [ ] **Step 8: Commit the helper and tests**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add \
  .agent/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py \
  tests/test_bootstrap_clever_work.py
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "feat: add template harness bootstrap metadata"
```

Expected: one commit for helper behavior and tests only

### Task 5: Mirror template/deploy metadata guidance in `clever-change-control`

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/README.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control/.github/ISSUE_TEMPLATE/change-request.yml`

- [ ] **Step 1: Update the README**

Document that change requests should also record:
- `template_id`
- `template_version`
- `deploy_profile`
- `lifecycle_action`

Explain that these values mirror the selected harness and are used for traceability, not as a separate source of truth.

- [ ] **Step 2: Extend the issue form guidance**

Add issue form fields or explicit guidance text for the same metadata. Keep the work-type taxonomy intact. Make it clear that the values should match the service lineage and bootstrap choice where applicable.

- [ ] **Step 3: Verify patch formatting in `clever-change-control`**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control diff --check -- \
  README.md \
  .github/ISSUE_TEMPLATE/change-request.yml
```

Expected: no output

- [ ] **Step 4: Commit the change-control contract updates**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control add \
  README.md \
  .github/ISSUE_TEMPLATE/change-request.yml
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control commit -m "docs: add template harness change metadata"
```

Expected: one commit for change-control guidance only

### Task 6: Final verification and reporting

**Files:**
- Review: all three repositories above

- [ ] **Step 1: Verify repo states**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project status --short
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo status --short
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control status --short
```

Expected:
- `clever-agent-project`: clean
- `clever-context-monorepo`: clean except for pre-existing unrelated local artifacts, if any
- `clever-change-control`: clean except for pre-existing unrelated local artifacts such as `.DS_Store`, if still present

- [ ] **Step 2: Run a final targeted verification pass**

Run:

```bash
pytest /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests/test_bootstrap_clever_work.py -q
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project diff --check
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo diff --check
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control diff --check
```

Expected:
- bootstrap helper tests pass
- all three repos report no patch-format errors

- [ ] **Step 3: Capture final commit hashes**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project rev-parse --short HEAD
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-context-monorepo rev-parse --short HEAD
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-change-control rev-parse --short HEAD
```

Expected: one short commit hash per repo
