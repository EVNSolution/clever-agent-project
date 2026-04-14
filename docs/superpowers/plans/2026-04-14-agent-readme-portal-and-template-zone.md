# Agent README Portal And Template Zone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework `clever-agent-project` so `README.md` becomes a short GitHub portal with a visible template-selection zone, while the detailed setup and operating instructions move into a new `docs/setting.md`.

**Architecture:** Keep the repo front door lightweight: `README.md` explains what this repo is, how 신규 개발 and 기존 서비스 변경 diverge, and where the template choices live. Move installation, bootstrap detail, metadata-reading rules, and folder-level explanation into `docs/setting.md`. Keep the existing workflow guide as a scenario document, and only touch it if the new portal/setting split creates wording drift.

**Tech Stack:** Markdown, Mermaid, GitHub collapsed sections (`<details>`), git, Python 3 for lightweight link verification

---

## File Map

- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md`

### Design Choice Locked By This Plan

- `README.md` stays as the GitHub landing page; it is not replaced by `setting.md`.
- The template area is rendered as a physically separated Markdown section, not hidden behind prose only.
- The complex Mermaid overview stays available from `README.md`, but inside a collapsed `<details>` block.
- `docs/setting.md` becomes the detailed operator guide for setup, bootstrap, metadata reading, and folder responsibilities.
- `docs/guides/clever-project-workflows.md` remains a scenario guide, not the place for installation/setup detail.

### Task 1: Create `docs/setting.md` as the detailed operator guide

**Files:**
- Create: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`

- [ ] **Step 1: Draft the section outline for `docs/setting.md`**

Create the file with these exact top-level sections:

```md
# CLEVER Agent Project Setting

## 이 문서의 역할
## 필수 사전 조건
## GitHub CLI 설치 및 인증
## Superpowers 설치
## Workspace 전제
## 먼저 읽을 문서 순서
## 신규 개발 시작 절차
## 기존 서비스 변경 / 유지보수 절차
## 템플릿과 메타 해석 기준
## Bootstrap Helper 사용 예시
## 폴더별 역할
## 관련 문서와 저장소
```

- [ ] **Step 2: Move detailed setup content from `README.md` into `docs/setting.md`**

Carry over and normalize:
- GitHub CLI install/auth instructions
- `superpowers` installation paths
- workspace root expectation
- helper command examples

Do not leave duplicate long-form setup instructions in `README.md`.

- [ ] **Step 3: Write the new detailed operating sections**

Document these exact behaviors:
- 신규 개발 starts by reviewing template candidates
- 유지보수 starts by reading service metadata from `clever-context-monorepo`
- `template_id`, `template_version`, `deploy_profile`, `override_scope`, `lifecycle_state` are the maintenance baseline
- changing template family is treated as migration

Include one expanded `flowchart TB` Mermaid diagram in `docs/setting.md` that covers:
- 사용자 요청
- work type branching
- template zone
- service metadata read
- bootstrap packet
- change-control recording
- target repo handoff

- [ ] **Step 4: Add folder-role explanations**

Add short responsibility notes for:
- `.agent/skills/bootstrap-clever-work/`
- `docs/`
- `scripts/`
- `tests/`

The descriptions must explain why a reader would open each area, not just restate the folder name.

- [ ] **Step 5: Verify the new file is structurally complete**

Run:

```bash
sed -n '1,260p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md
```

Expected: the file shows the new top-level sections, setup detail, and the expanded Mermaid block.

- [ ] **Step 6: Commit the `setting.md` guide**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add \
  docs/setting.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "docs: add agent setting guide"
```

Expected: one commit containing only the new detailed guide

### Task 2: Rewrite `README.md` as the GitHub portal

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`

- [ ] **Step 1: Replace the current long-form intro with a portal-style top section**

Rewrite the opening to state clearly:
- this repo is the CLEVER intake/bootstrap entry point
- authoritative workflow and service metadata live outside this repo
- `README.md` is for fast orientation, `docs/setting.md` is for detailed operation

Keep the opening concise enough to fit on one screen before the first long section.

- [ ] **Step 2: Add the two entry-path sections**

Create clearly separated sections for:
- `신규 개발 시작`
- `기존 서비스 변경`

Each section must explain:
- what the user does first
- whether template choice or service metadata is the first anchor
- which repo becomes authoritative next

- [ ] **Step 3: Add the visible template zone**

Create a physically separated template section using a Markdown table.

Use these seed rows exactly:

```md
| 템플릿 | 용도 | 배포 방식 | 상태 | 상세 |
| --- | --- | --- | --- | --- |
| `erik-project-template@v1` | 일반 서비스 시작용 예시 | 표준 웹/서비스 배포 기준 | `recommended` | `clever-context-monorepo` registry 연결 예정 |
| `msa-saas-standard@v1` | 복제형 SaaS 시작용 예시 | 고객사별 이미지 분기 운영 | `candidate` | registry 연결 예정 |
| `general-service-minimal@v1` | 경량 서비스 시작용 예시 | 단일 서비스 기준 | `candidate` | registry 연결 예정 |
| `custom candidate` | 비등록 템플릿 후보 | 선택 후 메타 기록 필요 | `candidate` | 사용자 지정 |
```

Follow the table with one short note:
- 신규는 여기서 템플릿을 보고 고른다.
- 유지보수는 기존 서비스 메타를 먼저 읽고, 필요하면 여기서 migration 후보를 다시 본다.

- [ ] **Step 4: Add the collapsed Mermaid overview**

Insert a `<details>` block with a `flowchart TB` Mermaid diagram that includes:
- 사용자 요청
- `clever-agent-project`
- 신규 / 유지보수 분기
- template zone
- service metadata read
- `clever-context-monorepo`
- `clever-change-control`
- target repo handoff

The diagram should be visually denser than the earlier simple draft and use Korean labels.

- [ ] **Step 5: Add the folder and document navigation blocks**

Add a short navigation section that links to:
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work/SKILL.md`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/.agent/skills/bootstrap-clever-work`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/scripts`
- `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/tests`

Keep each line to one responsibility sentence.

- [ ] **Step 6: Verify the rewritten `README.md`**

Run:

```bash
sed -n '1,260p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md
```

Expected: the file opens with a short portal introduction, shows the visible template zone, and contains a collapsed Mermaid section instead of long setup detail.

- [ ] **Step 7: Commit the portal rewrite**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add \
  README.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "docs: turn readme into agent portal"
```

Expected: one commit containing only the `README.md` rewrite

### Task 3: Align the workflow guide with the new portal/setting split

**Files:**
- Modify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Reference: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`

- [ ] **Step 1: Add a short orientation note near the top**

Add one short paragraph that distinguishes:
- `README.md` = landing portal
- `docs/setting.md` = setup and operating guide
- `docs/guides/clever-project-workflows.md` = scenario flow guide

- [ ] **Step 2: Remove or avoid setup duplication**

If the workflow guide currently implies setup/install detail, replace it with links to `docs/setting.md`. Do not duplicate installation steps here.

- [ ] **Step 3: Verify the workflow guide still reads as scenario guidance**

Run:

```bash
sed -n '1,220p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md
```

Expected: the file still focuses on project-start and change-control scenarios, with only a short pointer to the new portal/setting docs.

- [ ] **Step 4: Commit the workflow-guide alignment**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project add \
  docs/guides/clever-project-workflows.md
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project commit -m "docs: align workflow guide with portal docs"
```

Expected: one commit containing only the workflow-guide wording adjustment

### Task 4: Verify links, formatting, and final doc cohesion

**Files:**
- Verify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md`
- Verify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md`
- Verify: `/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md`

- [ ] **Step 1: Run markdown patch formatting verification**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project diff --check -- \
  README.md \
  docs/setting.md \
  docs/guides/clever-project-workflows.md
```

Expected: no output

- [ ] **Step 2: Verify linked local files exist**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
base = Path("/Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project")
required = [
    base / "README.md",
    base / "docs/setting.md",
    base / "docs/guides/clever-project-workflows.md",
    base / ".agent/skills/bootstrap-clever-work/SKILL.md",
    base / ".agent/skills/bootstrap-clever-work",
    base / "scripts",
    base / "tests",
]
missing = [str(path) for path in required if not path.exists()]
if missing:
    raise SystemExit("Missing paths:\\n" + "\\n".join(missing))
print("ok")
PY
```

Expected: `ok`

- [ ] **Step 3: Perform a final read-through of the three docs**

Run:

```bash
sed -n '1,220p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/README.md
sed -n '1,260p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/setting.md
sed -n '1,220p' /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project/docs/guides/clever-project-workflows.md
```

Expected:
- `README.md` reads like a landing page
- `docs/setting.md` reads like an operator guide
- `docs/guides/clever-project-workflows.md` reads like a scenario guide

- [ ] **Step 4: Commit the final verification state**

Run:

```bash
git -C /Users/jiin/Documents/Files/02_EVnSolution/00_Source_code/CLEVER/clever-agent-project status --short
```

Expected: only the intended doc changes remain staged or committed; no unrelated file changes are introduced.
