# CLEVER Agent Project

> CLEVER는 단일 레포지토리 에이전트가 아니다.  
> 로컬에 함께 내려받은 3개 레포지토리를 함께 읽고, 이후 실제 구현 대상 레포지토리로 실행을 넘기는 워크스페이스 우선 제어 평면 런타임이다.

## 사용 환경별 시작

CLEVER는 한 가지 앱 전용 흐름이 아니다. 사용자가 익숙한 도구에 따라 시작 방식이 다르다.
첫 화면에서는 직접 shell 명령보다 **어떤 환경에서 시작하는지**를 먼저 고른다.
공통 원칙은 **3개 레포를 같은 로컬 workspace에 두고, 일반 시작은 `clever-agent-project`에서 진행한다**는 점이다.

브라우저에서 버튼과 텍스트 입력으로 한 번에 정리하려면 [GitHub Pages 시작 도우미](https://evnsolution.github.io/clever-agent-project/start/)를 사용한다. 버튼과 텍스트 입력으로 답한 뒤 최종 copy text를 만들고, 에이전트에 붙여 넣을 위치까지 안내한다.

<details>
<summary><strong>앱형 에이전트 / Application</strong> — 채팅에 프롬프트를 붙여 넣고 기본 세팅을 맡긴다.</summary>

앱형 에이전트는 LLM과 대화하듯이 세팅을 맡긴다. 사용자가 터미널 명령을 직접 관리하기 어렵다면, 앱 채팅에 아래 프롬프트를 그대로 붙여 넣는다.

```text
CLEVER 작업을 시작하고 싶어.

먼저 `gh auth status`와 `gh api user --jq .login`으로 현재 GitHub 계정을 확인해줘.
gh CLI에서 계정을 확인할 수 있으면 별도로 묻지 말고 그 계정으로 preflight를 진행해줘.
GitHub 계정을 확인할 수 없거나 다른 계정을 써야 할 때만 물어봐줘.
그 다음 내 로컬 환경에서 가능한지 확인하고, 가능하면 기본 세팅을 네가 진행해줘.

해야 할 일:
1. 현재 로컬 workspace 위치를 확인해줘. 정해진 위치가 없으면 `clever-agent-workspace`를 만들어줘.
2. workspace 안에 3개 repo가 있는지 확인하고, 없는 repo만 아래 주소로 clone해줘.
   mkdir -p clever-agent-workspace
   cd clever-agent-workspace
   test -d clever-agent-project || git clone https://github.com/EVNSolution/clever-agent-project.git
   test -d clever-context-monorepo || git clone https://github.com/EVNSolution/clever-context-monorepo.git
   test -d clever-change-control || git clone https://github.com/EVNSolution/clever-change-control.git
   cd clever-agent-project
3. 일반 작업 시작 위치는 `clever-agent-project`로 맞춰줘.
4. preflight는 우선 `CLEVER_EXPECTED_GITHUB_LOGIN` 없이 아래 명령으로 실행해줘.
   python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
5. GitHub 계정 확인이 실패하거나 내가 다른 계정을 지정한 경우에만 `CLEVER_EXPECTED_GITHUB_LOGIN`을 사용해줘.
6. 필요한 shell 명령은 네가 실행하고 결과를 확인해줘.
7. preflight 결과가 실패하면 바로 작업 질문으로 넘어가지 말고, 무엇이 부족한지 먼저 설명해줘.
8. preflight가 통과하면 README의 "작업 시작" 양식으로 내 요구사항을 정리해줘.
```

앱이 로컬 파일이나 shell 실행을 지원하지 않으면, 에이전트가 직접 세팅할 수 없다. 그 경우에는 터미널 가능한 환경에서 3개 repo clone과 preflight를 먼저 끝낸 뒤, 결과를 앱에 붙여 넣는다.

</details>

<details>
<summary><strong>VS Code Extension</strong> — 확장 채팅과 Integrated Terminal로 기본 세팅을 맡긴다.</summary>

VS Code Extension도 확장 채팅에 세팅을 맡긴다. 사용자는 VS Code에서 workspace만 열고, 확장 채팅에 아래 프롬프트를 그대로 붙여 넣는다.

```text
CLEVER 작업을 VS Code Extension에서 시작하고 싶어.

먼저 `gh auth status`와 `gh api user --jq .login`으로 현재 GitHub 계정을 확인해줘.
gh CLI에서 계정을 확인할 수 있으면 별도로 묻지 말고 그 계정으로 preflight를 진행해줘.
GitHub 계정을 확인할 수 없거나 다른 계정을 써야 할 때만 물어봐줘.
그 다음 VS Code의 Integrated Terminal을 사용해서 기본 세팅을 네가 진행해줘.

해야 할 일:
1. 현재 VS Code workspace가 어디인지 확인해줘.
2. workspace 안에 3개 repo가 있는지 확인하고, 없는 repo만 Integrated Terminal에서 아래 주소로 clone해줘.
   mkdir -p clever-agent-workspace
   cd clever-agent-workspace
   test -d clever-agent-project || git clone https://github.com/EVNSolution/clever-agent-project.git
   test -d clever-context-monorepo || git clone https://github.com/EVNSolution/clever-context-monorepo.git
   test -d clever-change-control || git clone https://github.com/EVNSolution/clever-change-control.git
   cd clever-agent-project
3. 일반 작업 시작 위치는 `clever-agent-project`로 맞춰줘.
4. preflight는 우선 `CLEVER_EXPECTED_GITHUB_LOGIN` 없이 아래 명령으로 실행해줘.
   python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
5. GitHub 계정 확인이 실패하거나 내가 다른 계정을 지정한 경우에만 `CLEVER_EXPECTED_GITHUB_LOGIN`을 사용해줘.
6. Integrated Terminal에서 preflight를 실행하고 결과를 읽어줘.
7. preflight가 실패하면 부족한 설정을 먼저 고쳐줘.
8. preflight가 통과하면 README의 "작업 시작" 양식으로 내 요구사항을 정리해줘.
```

확장이 shell 명령을 직접 실행하지 못하면, Integrated Terminal에 실행할 명령을 제시하게 하고 사용자가 결과를 다시 붙여 넣는다.

</details>

<details>
<summary><strong>터미널 CLI</strong> — 개발자처럼 직접 작업 디렉토리에서 시작한다.</summary>

터미널 CLI는 개발자처럼 직접 작업 디렉토리에서 시작한다. Codex CLI, Claude Code, Gemini CLI처럼 shell을 직접 쓰는 사용자는 아래 명령을 직접 실행한다.

#### 터미널 CLI용 직접 설정 명령

아래 명령은 터미널 CLI 사용자를 위한 직접 설정용이다. 앱형 에이전트나 VS Code Extension 사용자는 위 프롬프트를 먼저 사용한다.

```bash
mkdir -p clever-agent-workspace
cd clever-agent-workspace

git clone https://github.com/EVNSolution/clever-agent-project.git
git clone https://github.com/EVNSolution/clever-context-monorepo.git
git clone https://github.com/EVNSolution/clever-change-control.git

cd clever-agent-project
python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

에이전트 종류별 실행 예시:

```bash
# Codex
codex --yolo

# Claude Code
claude --dangerously-skip-permissions

# Gemini CLI
gemini --yolo
```

gh CLI에서 GitHub 계정이 확인되면 별도로 묻지 않는다. 다른 계정으로 고정 검증해야 할 때만 아래처럼 `CLEVER_EXPECTED_GITHUB_LOGIN`을 붙인다.

```bash
CLEVER_EXPECTED_GITHUB_LOGIN="<github-login-or-profile-url>" \
  python3 scripts/bootstrap_clever_work.py --cwd "$PWD" --preflight --json
```

`preflight_check.ready=true`이면 CLI 에이전트를 열고 [시작 입력](#시작-입력)을 붙여 넣거나 자연어로 설명한다.

</details>

## 시작 입력

아래 양식을 채워도 되고, 자연어로 편하게 설명해도 된다.
혹은 자연어로 편하게 대화하며 진행하세요.
에이전트가 내용을 시작 분기로 다시 정리하고, 부족한 값만 추가로 묻는다.

처음 입력에서는 전문 용어를 몰라도 된다. 먼저 쉬운 말로 세 가지만 잡는다.

1. **작업 성격**: 신규 개발, 기능 수정, 버그 수정, 리팩터링, 문서/운영 정리 중 어디에 가까운가?
2. **대상 범위**: 앱/서비스/기능, 화면, API, DB/model, CI/CD, 문서/운영 중 어디인가?
3. **목표 수준**: 요구사항, 설계, 계획, 코드 변경, 테스트, 배포/운영 중 어디까지 원하는가?

MONO/MSA, `target_service`, 배포 범위 같은 전문 용어는 첫 입력에서 묻지 않는다. 에이전트가 설명을 읽고 내부적으로 정리하거나, 꼭 필요할 때만 나중에 좁혀 묻는다.

```text
작업 시작

먼저 하려는 일을 한 줄로 적어 주세요.
선택지에 맞춰 답해도 되고, 애매하면 문장으로 편하게 설명해도 됩니다.

- 하려는 일:

아래 항목은 모르면 `아직 모름`으로 둬도 됩니다.
각 항목은 선택지 중 하나를 골라도 되고, 선택지에 딱 맞지 않으면 직접 설명해도 됩니다.

1. 작업 성격은 어디에 가깝나요?
- 신규 개발
- 기존 기능 확장/수정
- 버그 수정
- 리팩터링/구조 개선
- 문서/설정/운영 정리
- 아직 모름
- 직접 설명:

2. 대상 범위는 무엇인가요?
- 새 앱/서비스/기능
- 기존 앱/서비스/기능
- 화면/UI
- API
- DB/model
- CI/CD 또는 배포 workflow
- 문서/운영 설정
- 아직 모름
- 직접 설명:

3. 이번 작업의 목표 수준은 어디까지인가요?
- 요구사항 정리
- 설계 문서 작성
- 구현 계획 수립
- 실제 코드 변경
- 테스트/검증
- 배포/운영 준비
- 1차 MVP 개발 및 배포
- 운영 반영
- 아직 모름
- 직접 설명:

4. 알고 있는 이름이나 링크가 있나요? 없으면 비워도 됩니다.
- repo:
- service/app:
- 화면:
- API:
- DB/model:
- 문서:
- issue/PR/Figma/회의 메모/에러 로그:

5. 현재 상태를 알고 있나요? 모르면 `아직 모름`으로 둬도 됩니다.
- 이미 되어 있는 것:
- 아직 없는 것:
- 먼저 확인해야 할 것:

6. 주의할 점이 있나요? 없으면 비워도 됩니다.
- 꼭 지킬 것:
- 피할 것:
- 건드리면 안 되는 범위:
- 보안/운영/배포 관련 주의사항:
```

자연어 예시:

```text
회원가입, 로그인, 사용자 확인 기능이 있는 단순한 인증 시스템을 만들고 싶다.
작업 성격은 신규 개발이고, 대상 범위는 새 앱/서비스/기능이다.
이번에는 실제 코드 변경까지 하고 싶고, 권한 관리나 소셜 로그인은 나중에 하고 싶다.
```

에이전트는 이 입력을 시작 분기로 해석하고, 먼저 startup branch state를 채운 뒤에만 `project-start` 초안, repo bootstrap, 구현 계획으로 내려간다.
