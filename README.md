# clever_agent_project

CLEVER 작업을 시작할 때 사용하는 repo-local 에이전트 자산 저장소다.

## 목적

이 저장소는 전역 superpowers 설치에 의존하지 않고, CLEVER 전용 스킬과 보조 파일을 repo 안에서 함께 관리하기 위한 시작점이다.

## Superpowers 설치

이 저장소와 이후 생성되는 target repo 세션은 Codex에 `superpowers`가 설치되어 있다는 전제로 동작한다.

### 권장 설치 방식

새 Codex 세션에서 아래 요청을 실행한다.

```text
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.codex/INSTALL.md
```

### 수동 설치 방식

필요하면 공식 Codex 문서 기준으로 수동 설치할 수 있다.

```bash
git clone https://github.com/obra/superpowers.git ~/.codex/superpowers
mkdir -p ~/.agents/skills
ln -s ~/.codex/superpowers/skills ~/.agents/skills/superpowers
```

설치 후에는 Codex를 재시작한다.

subagent 기반 스킬까지 쓰려면 Codex 설정에 multi-agent 기능을 켠다.

```toml
[features]
multi_agent = true
```

### 새 프로젝트 repo에서 어떻게 적용되는가

새 프로젝트 repo를 만들 때마다 `superpowers`를 repo 안에 다시 설치하는 모델은 아니다.

운영 방식은 아래와 같다.

1. 사용자 Codex 환경에 `superpowers`를 한 번 설치한다.
2. CLEVER 작업 시작은 `clever_agent_project`에서 한다.
3. 승인 후 target GitHub repo를 생성하고 로컬에 clone 또는 pull 한다.
4. 그 target repo 루트에서 새 Codex 세션을 시작한다.
5. 새 세션은 이미 설치된 `superpowers` 스킬을 자동으로 사용한다.

즉, `superpowers`는 사용자 Codex 환경에 설치되고, 새 프로젝트 repo는 그 환경 위에서 실행되는 작업 대상 repo가 된다.

## 실행 가이드

새 CLEVER 작업은 이 저장소를 intake surface로 사용한다.

### 사전 조건

CLEVER 관련 저장소는 하나의 workspace root 아래에 두는 것을 권장한다.

```text
<CLEVER_ROOT>/
  clever_agent_project/
  clever-change-control/
  clever-context-monorepo/
```

세션은 `<CLEVER_ROOT>/clever_agent_project`에서 시작한다.

### 먼저 읽을 순서

초안을 만들기 전에 아래 순서대로 읽는다.

1. 이 `README.md`
2. `.codex/skills/bootstrap-clever-work/SKILL.md`
3. `clever-change-control`과 `clever-context-monorepo`의 현재 SSOT 상태

이 순서가 끝나기 전에는 계획 수립이나 구현으로 들어가지 않는다.

### 1단계: Bootstrap Packet 생성

`clever_agent_project`에서 repo-local helper를 실행한다.

```bash
python3 .codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py --cwd "$PWD" --json
```

사용자가 목적, 제약, 기대 결과, target repo를 이미 줬다면 함께 넘긴다.

```bash
python3 .codex/skills/bootstrap-clever-work/scripts/bootstrap_clever_work.py \
  --cwd "$PWD" \
  --purpose "<purpose>" \
  --constraints "<constraints>" \
  --expected-result "<expected result>" \
  --target-repo "<target repo if known>" \
  --json
```

기대 출력은 아래 네 축이다.

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`
- `ssot_docs_read`

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

`clever_agent_project`는 intake와 orchestration surface다. 승인된 packet이 명시적으로 그렇게 정하지 않는 한, 기본 실행 repo로 취급하지 않는다.

### 하지 말아야 할 것

- canonical `change_id`를 만들지 않는다.
- 시작 초안 전에 `target_service`를 필수로 요구하지 않는다.
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

- `.codex/skills/bootstrap-clever-work/`

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

- `project_start_issue`
- `repo_bootstrap`
- `repo_session_handoff`

일반 start path에서는 canonical `change_id`를 만들지 않고, service-doc 생성 작업도 준비하지 않는다.

## 저장소 구조

```text
.codex/
  skills/
    bootstrap-clever-work/
      SKILL.md
      agents/openai.yaml
      scripts/bootstrap_clever_work.py
```

## 참고

- 이 저장소는 CLEVER 기여자들과 공유하는 것을 전제로 한다.
- 스킬은 의도적으로 repo-local이다. 사용자별 전역 skills 디렉터리에 두는 모델이 아니다.
