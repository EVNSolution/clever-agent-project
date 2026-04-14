# clever-agent-project

CLEVER 작업을 시작할 때 사용하는 repo-local 에이전트 자산 저장소다.

## 목적

이 저장소는 CLEVER 작업의 intake, bootstrap, handoff를 표준화하기 위한 시작점이다. repo-local bootstrap 자산은 이 저장소에 두고, 일반적인 설계 및 구현 워크플로우는 설치된 `superpowers`를 통해 실행한다.

## 작업 운영 규칙

이 저장소는 `main` 기준 direct push 운영을 기본으로 한다. 승인 후 변경 내용을 `main`에 바로 반영하되 PR은 생성하지 않는다. 필요 시 사용자가 별도로 요청할 때만 PR 워크플로우를 사용한다.

## 필수 사전 조건

이 저장소를 실제로 운용하려면 아래 조건이 필요하다.

1. `superpowers`가 설치된 지원 에이전트 런타임 하나
2. `git`
3. `python3`
4. `gh` (GitHub CLI)
5. 같은 workspace root 아래의 `clever-agent-project`, `clever-change-control`, `clever-context-monorepo`

`bootstrap_clever_work.py`는 `git`과 `python3`에 직접 의존한다. 승인 후 실제 운영 흐름은 `gh` 기반의 GitHub 인증, 이슈 생성, repo 생성 또는 확인 작업을 전제로 한다.

## GitHub CLI 설치 및 인증

GitHub CLI는 GitHub 공식 설치 경로를 따르는 것을 권장한다.

- 설치 개요: <https://github.com/cli/cli#installation>
- 명령어 매뉴얼: <https://cli.github.com/manual/>

### macOS

```bash
brew install gh
brew upgrade gh
```

### Windows

```powershell
winget install --id GitHub.cli
winget upgrade --id GitHub.cli
```

### Linux

#### Debian / Ubuntu / Raspberry Pi

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O "$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

#### Fedora / RHEL / openSUSE / SUSE 계열

대표적인 공식 RPM 설치 방식은 아래와 같다.

```bash
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh --repo gh-cli
```

DNF4, `yum`, `zypper` 등 다른 공식 RPM 계열 설치 방식은 GitHub CLI Linux 설치 문서를 따른다.

### 인증

기본 인증 흐름은 브라우저 기반 로그인이다.

```bash
gh auth login
gh auth setup-git
gh auth status
```

헤드리스 환경에서는 `GH_TOKEN` 환경 변수 또는 `gh auth login --with-token` 방식을 사용할 수 있다.

## Superpowers 설치

이 저장소는 Codex 전용이 아니다. `superpowers`가 설치된 지원 에이전트 런타임이면 같은 시작 흐름을 사용할 수 있다.

`/.agent` 폴더는 에이전트용 메타데이터를 담는 위치일 뿐이며, 저장소 운영의 필수 실행 체인은 아닙니다.

현재 README 기준으로 확인 가능한 설치 경로는 아래와 같다.

### Claude Code Official Marketplace

```bash
/plugin install superpowers@claude-plugins-official
```

### Claude Code (via Plugin Marketplace)

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### Cursor (via Plugin Marketplace)

```text
/add-plugin superpowers
```

또는 plugin marketplace에서 `superpowers`를 검색해 설치한다.

### Codex

```text
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.codex/INSTALL.md
```

세부 문서: <https://github.com/obra/superpowers/blob/main/docs/README.codex.md>

### OpenCode

```text
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
```

세부 문서: <https://github.com/obra/superpowers/blob/main/docs/README.opencode.md>

### Gemini CLI

```bash
gemini extensions install https://github.com/obra/superpowers
```

업데이트:

```bash
gemini extensions update superpowers
```

지원 런타임에서 subagent 기능이 있다면 켜는 것을 권장하지만, 이 저장소를 시작점으로 쓰기 위한 절대 필수 조건은 아니다.

### 새 프로젝트 repo에서 어떻게 적용되는가

새 프로젝트 repo를 만들 때마다 `superpowers`를 repo 안에 다시 설치하는 모델은 아니다.

운영 방식은 아래와 같다.

1. 사용 중인 에이전트 환경에 `superpowers`를 한 번 설치한다.
2. CLEVER 작업 시작은 `clever-agent-project`에서 한다.
3. 승인 후 target GitHub repo를 생성하고 로컬에 clone 또는 pull 한다.
4. 그 target repo 루트에서 같은 에이전트 런타임으로 새 세션을 시작한다.
5. 새 세션은 이미 설치된 `superpowers`를 사용해 후속 계획 및 구현을 진행한다.

즉, `superpowers`는 사용자 에이전트 환경에 설치되고, 새 프로젝트 repo는 그 환경 위에서 실행되는 작업 대상 repo가 된다.

## 실행 가이드

새 CLEVER 작업은 이 저장소를 intake surface로 사용한다.

### Markdown으로 이슈 제목/본문 직접 수정하기

이슈 제목과 본문 타입 규칙을 유지하려면, Markdown front matter를 수정한 뒤 동기화 스크립트를 실행한다.

1. 템플릿 복사 또는 기존 draft 파일 수정
   - 템플릿: `docs/templates/issue-edit-template.md`
   - 현재 project-start draft 예시: `docs/issue-drafts/project-start-3.md`
2. front matter의 아래 필드를 수정
   - `repo`
   - `issue_number`
   - `work_type_group` (`MSA/SaaS`, `일반 개발`)
   - `work_type_detail`
     - `MSA/SaaS`: `복제`, `수정`, `변경`, `신규`
     - `일반 개발`: `신규 개발`, `수정`, `변경`, `리팩토링`
   - `title` - 가능한 한 짧은 명사구로 적는다
3. dry-run으로 결과 확인

```bash
python3 scripts/sync_issue_from_md.py docs/issue-drafts/project-start-3.md --dry-run
```

4. 실제 반영

```bash
python3 scripts/sync_issue_from_md.py docs/issue-drafts/project-start-3.md
```

스크립트는 제목을 자동으로 `[상위 타입][하위 타입] 짧은 제목` 형태로 조합해 GitHub 이슈를 갱신한다.

예:

- `[MSA/SaaS][복제] 배차 서비스 고객사 배포 분기 추가`
- `[일반 개발][리팩토링] bootstrap packet 구조 정리`

이슈 본문에도 같은 타입을 남겨야 한다.

```text
work_type_group: MSA/SaaS
work_type_detail: 복제
```

에이전트는 제목과 본문의 타입 값을 항상 일치시켜야 한다.

스크립트는 문장형 종결어를 가능한 범위에서 걷어내고, 너무 긴 제목은 잘라서 추적하기 쉬운 길이로 정리한다.

### 사전 조건

CLEVER 관련 저장소는 하나의 workspace root 아래에 두는 것을 권장한다.

```text
<CLEVER_ROOT>/
  clever-agent-project/
  clever-change-control/
  clever-context-monorepo/
```

세션은 `<CLEVER_ROOT>/clever-agent-project`에서 시작한다.

### 먼저 읽을 순서

초안을 만들기 전에 아래 순서대로 읽는다.

1. 이 `README.md`
2. `.agent/skills/bootstrap-clever-work/SKILL.md`
3. `clever-change-control`과 `clever-context-monorepo`의 현재 SSOT 상태

이 순서가 끝나기 전에는 계획 수립이나 구현으로 들어가지 않는다.

### 작업 성격 먼저 분류

시작점은 항상 `clever-agent-project`지만, 모든 작업이 같은 분기를 타지는 않는다.

#### MSA/SaaS 복제형 작업

아래 성격이면 이 분기로 본다.

- 플랫폼 템플릿과 배포 표준을 바탕으로 서비스를 복제한다.
- 고객사별로 수정/변경을 얹어 SaaS 형태로 전개한다.
- 컨테이너마다 다른 이미지를 올리는 운영 구조를 염두에 둔다.

이 경우에는 일반 bootstrap을 바로 밀어붙이지 말고 아래 순서로 진행한다.

1. 대화로 target service 또는 대상 서비스 군을 먼저 정한다.
2. `clever-context-monorepo/docs/root/msa-saas-replication-governance.md`를 읽는다.
3. `clever-context-monorepo/docs/root/clever-msa-platform-workspace.md`를 읽는다.
4. target service가 정해졌으면 `clever-context-monorepo/docs/services/<service-name>/index.md`를 읽는다.
5. 그 다음 일반 bootstrap과 target repo handoff 흐름으로 이어간다.

#### 일반 개발 작업

위 분류에 속하지 않는 일반적인 신규 개발, 수정, 변경, 리팩토링, 특정 repo 구현 작업은 기존 시작 흐름을 그대로 사용한다.

- 시작 시 `target_service`를 먼저 확정할 필요는 없다.
- 아래 bootstrap packet 생성부터 진행한다.

### 템플릿 선택 규칙

작업 성격 분기 뒤에는 신규 개발과 유지보수 모두에서 템플릿 선택지를 항상 사용자에게 보여준다.

- template registry 정본은 `clever-context-monorepo/docs/templates/index.md`에 둔다.
- 전역 규칙은 `clever-context-monorepo/docs/root/template-harness-governance.md`를 따른다.
- deploy baseline은 `clever-context-monorepo/docs/root/deploy-template-governance.md`를 따른다.
- 유지보수면 먼저 `clever-context-monorepo/docs/services/<service-name>/index.md`의 template lineage를 읽고, 기존 `template_id`/`template_version`을 기본 추천으로 제시한다.
- 그래도 선택지는 항상 보여주고 최종 선택은 사용자에게 맡긴다.
- 기존 템플릿과 다른 template/version으로 가면 일반 수정이 아니라 `migration` 성격으로 기록한다.

### 1단계: Bootstrap Packet 생성

`clever-agent-project`에서 repo-local helper를 실행한다.

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --template-id "<template id>" \
  --template-version "<version>" \
  --deploy-profile "<deploy profile>" \
  --override-scope "<override scope>" \
  --lifecycle-action "<adopt|modify|migrate|retire>" \
  --json
```

사용자가 목적, 제약, 기대 결과, target repo를 이미 줬다면 함께 넘긴다.

```bash
python3 scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --purpose "<purpose>" \
  --constraints "<constraints>" \
  --expected-result "<expected result>" \
  --target-repo "<target repo if known>" \
  --template-id "<template id>" \
  --template-version "<version>" \
  --deploy-profile "<deploy profile>" \
  --override-scope "<override scope>" \
  --lifecycle-action "<adopt|modify|migrate|retire>" \
  --json
```

루트에 있는 `scripts/bootstrap_clever_work.py`는 같은 명령을 래핑한 진입점이라
초기 세션에서도 `.agent` 경로를 직접 건드리지 않아도 된다.

기대 출력은 아래 네 축이다.

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`
- `ssot_docs_read`

packet과 issue draft에는 아래 template metadata도 포함한다.

- `template_id`
- `template_version`
- `deploy_profile`
- `override_scope`
- `lifecycle_action`

### 2단계: 승인 게이트 제시

packet 요약을 사용자에게 보여주고 아래 질문 한 번만 한다.

> 아래 project-start 초안과 repo bootstrap 제안으로 진행할까요? 틀리면 수정할 필드만 말해 주세요.

승인 전에는 GitHub issue, repo, branch, folder, SSOT 변경을 만들지 않는다.

### 3단계: 승인 후 실행 순서

승인 후 순서는 아래와 같다.

1. `clever-change-control`에 `project-start` 이슈를 생성한다.
2. 생성된 `project-start issue #`를 canonical identifier로 사용한다.
3. target repo를 제안하거나 확정한다.
4. 필요하면 대상 GitHub repo를 생성한다.
5. target repo를 로컬에 clone 또는 pull 한다.
6. target repo를 기준으로 새 세션으로 handoff 한다.

### 4단계: Handoff 원칙

기본값은 target repo에서 새 세션을 시작하는 것이다.

`clever-agent-project`는 intake와 orchestration surface다. 승인된 packet이 명시적으로 그렇게 정하지 않는 한, 기본 실행 repo로 취급하지 않는다.

### 하지 말아야 할 것

- canonical `change_id`를 만들지 않는다.
- 시작 초안 전에 `target_service`를 필수로 요구하지 않는다.
- 일반 개발 작업에 MSA/SaaS 복제 규칙을 기본값으로 강제하지 않는다.
- 일반 start path에서 service-doc draft를 만들지 않는다.
- 일반 프로젝트 intake 중 SSOT source를 수정하지 않는다.
- 승인 게이트를 건너뛰지 않는다.

### 사용자용 흐름 설명 문서

아래 문서는 사용자 관점에서 정리되어 있다.

- 언제 새 `project-start`를 만드는지
- 언제 기존 `project-start` 아래 child issue로 가는지
- 새 프로젝트 시작과 기존 repo 개선/재구현이 어떻게 다른지

문서:

- `docs/guides/clever-project-workflows.md`

## 현재 자산

- `.agent/skills/bootstrap-clever-work/`

`bootstrap-clever-work` 스킬은 아래 두 저장소를 SSOT로 보고 시작 흐름을 표준화한다.

- `clever-context-monorepo`: 규칙과 workflow SSOT
- `clever-change-control`: 변경 기록과 추적 SSOT

이 스킬은 더 이상 생성된 `change_id`나 추론된 `target_service`에서 시작하지 않고, `project-start` 초안에서 시작한다.

일반적인 흐름은 아래와 같다.

1. `project-start` 초안을 만든다.
2. 승인을 받는다.
3. 이슈를 생성한다.
4. target repo bootstrap을 제안한다.
5. target repo를 로컬에 clone 또는 pull 한다.
6. target repo에서 새 세션 시작을 권장한다.

생성 이후의 canonical identifier는 `project-start issue #`다. 이슈 생성 전까지 helper는 repo-local draft packet만 만든다.

MSA/SaaS 복제형 작업은 예외적으로 target service 대화와 `clever-context-monorepo` root/service 문서 확인이 bootstrap보다 앞설 수 있다. 다만 이 경우에도 canonical identifier는 동일하게 `project-start issue #`를 사용한다.

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`

일반 start path에서는 canonical `change_id`를 만들지 않고, service-doc 생성 작업도 준비하지 않는다.

## 저장소 구조

```text
.agent/
  skills/
    bootstrap-clever-work/
      SKILL.md
      agents/openai.yaml
      scripts/bootstrap_clever_work.py
```

## 참고

- 이 저장소는 CLEVER 기여자들과 공유하는 것을 전제로 한다.
- 스킬은 의도적으로 repo-local이다. 사용자별 전역 skills 디렉터리에 두는 모델이 아니다.
