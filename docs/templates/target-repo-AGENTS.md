# AGENTS.md

## 이 파일의 역할

이 파일은 프로젝트 기획서가 아니다.

이 파일은 이 target repo에서 agent가 작업을 수행할 때 따라야 하는 실행 절차서다.
기획, 제품 범위, 사용자 가치, 미정 요구사항은 `docs/project-brief.md`에 둔다.

## 프로젝트 연결값

- project-start issue: `<project_start_issue>`
- change-control issue: `<change_control_issue>`
- target repo: `<target_repo>`
- target service: `<target_service>`
- template lineage: `<template_lineage>`
- default work branch: `<default_work_branch>`

값이 아직 확정되지 않은 항목은 `pending`으로 남기고, 추측해서 채우지 않는다.

## 저장소 역할

이 저장소는 구현 대상 repo다.

- 해석 정본: `clever-context-monorepo`
- 승인과 추적 정본: `clever-change-control`
- 시작과 bootstrap 정본: `clever-agent-project`

이 repo 안에서는 제품 코드, 테스트, 로컬 구현 문맥만 관리한다.
전역 규칙을 바꾸거나 서비스 정본을 갱신해야 하면 `clever-context-monorepo`에서 처리한다.

## 작업 시작 순서

새 세션 또는 새 이슈 작업을 시작하면 아래 순서로 진행한다.

1. `git status --short --branch`로 branch와 dirty 상태를 확인한다.
2. 현재 작업이 연결된 issue를 확인한다.
3. `project-start issue`와 `change-control issue`가 연결되어 있는지 확인한다.
4. 현재 branch가 작업 범위와 맞는지 확인한다.
5. `docs/project-brief.md`에서 프로젝트 목적과 제약을 확인한다.
6. 필요한 경우 `clever-context-monorepo/docs/services/<service>/index.md`를 읽는다.
7. 작업 전 변경 범위와 검증 방법을 짧게 정리한다.
8. 기능 변경 또는 버그 수정은 테스트를 먼저 추가한다.
9. 구현한다.
10. 관련 테스트와 `git diff --check`를 실행한다.
11. context monorepo 반영 필요 여부를 확인한다.
12. 완료 보고에 변경 내용, 검증 결과, 남은 리스크를 남긴다.

## Branch 운영

- `main`: deploy branch다.
- `dev`: 통합 작업 branch다.
- task branch: 이슈 또는 작업 단위 branch다.

초기 remote bootstrap 후에는 `dev`를 만들고, 이후 일반 작업은 `dev` 또는 task branch에서 진행한다.
`dev`가 생긴 뒤에는 `main`에 직접 push하지 않는다.

## GitHub Ruleset 운영

새 프로젝트 repo는 public으로 만든다.
GitHub Free 조직에서 private repo ruleset은 enforce되지 않는다.

새 repo bootstrap 후 초기 `main` commit과 `dev` branch push가 끝나면 아래 명령으로 GitHub ruleset을 적용한다.

```bash
chmod +x scripts/apply-github-rulesets.sh
scripts/apply-github-rulesets.sh <target_repo_full_name>
```

표준 ruleset:

- main: PR 경유만 허용. direct push는 GitHub ruleset에서 막는다. 승인 수는 0명으로 둔다.
- dev: PR 1명 이상 승인 필요.
- 그 외 branch: GitHub ruleset 미적용. 자유롭게 push할 수 있다.

적용 스크립트는 `gh api`를 사용한다.
실행 계정에는 target repo의 GitHub Administration write 권한이 필요하다.
private repo로 만들어야 하는 예외가 생기면 ruleset enforce가 되지 않는 리스크를 먼저 이슈에 남긴다.

## 브랜치 역할별 접두사

task branch는 프로젝트명이나 repo명으로 시작하지 않는다.
`clever-` 같은 제품/조직/프로젝트 이름은 branch 역할 접두사가 아니다.
필요하면 topic 뒤에만 넣는다.

허용 branch:

- `main`: deploy branch
- `dev`: integration work branch
- `feature/<issue-or-cc>-<short-topic>`: 신규 기능
- `fix/<issue-or-cc>-<short-topic>`: 버그 수정
- `change/<issue-or-cc>-<short-topic>`: 동작 변경
- `refactor/<issue-or-cc>-<short-topic>`: 구조 개선
- `docs/<issue-or-cc>-<short-topic>`: 문서 작업
- `chore/<issue-or-cc>-<short-topic>`: 설정, 관리, 빌드 보조 작업
- `test/<issue-or-cc>-<short-topic>`: 테스트 보강
- `release/<env-or-version>`: 릴리스 준비
- `hotfix/<issue-or-cc>-<short-topic>`: 긴급 수정

예:

- 좋음: `feature/issue-24-login-timeout`
- 좋음: `fix/cc-12-issue-24-login-timeout`
- 나쁨: `clever-login-timeout`
- 나쁨: `issue-24-login-timeout`

브랜치 역할 접두사를 로컬에서 강제하려면 target repo에서 아래 명령을 실행한다.

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"
case "$branch" in
  main|dev|feature/*|fix/*|change/*|refactor/*|docs/*|chore/*|test/*|release/*|hotfix/*)
    exit 0
    ;;
  *)
    echo "Invalid branch name: $branch"
    echo "Use main, dev, or a role-prefixed task branch:"
    echo "feature/* fix/* change/* refactor/* docs/* chore/* test/* release/* hotfix/*"
    exit 1
    ;;
esac
EOF
chmod +x .git/hooks/pre-commit

cat > .git/hooks/pre-push <<'EOF'
#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"
case "$branch" in
  main)
    echo "Direct pushes to main are blocked locally. Use dev or a role-prefixed task branch."
    exit 1
    ;;
  dev|feature/*|fix/*|change/*|refactor/*|docs/*|chore/*|test/*|release/*|hotfix/*)
    exit 0
    ;;
  *)
    echo "Invalid branch name: $branch"
    echo "Use dev or a role-prefixed task branch:"
    echo "feature/* fix/* change/* refactor/* docs/* chore/* test/* release/* hotfix/*"
    exit 1
    ;;
esac
EOF
chmod +x .git/hooks/pre-push
```

`pre-commit`은 잘못된 branch 이름에서 commit 생성을 막는다.
`pre-push`는 `main` direct push와 잘못된 branch 이름 push를 막는다.

## Issue 연결 규칙

작업을 시작하기 전에 아래 연결을 확인한다.

- `clever-change-control` issue가 root `project-start issue`를 언급한다.
- target repo issue가 `clever-change-control` issue를 언급한다.
- branch 이름 또는 PR 설명에서 관련 issue를 추적할 수 있다.

GitHub 자동 링크만으로 충분하다고 보지 않는다.
이슈 코멘트 또는 PR 설명에 현재 상태, branch, commit, 다음 action을 명시한다.

## 구현 규칙

- 기존 코드 스타일과 도구를 우선한다.
- 새 abstraction은 중복이나 복잡도를 실제로 줄일 때만 추가한다.
- config, env, deploy contract를 바꾸면 문서 반영 필요 여부를 같이 본다.
- public contract, API, 데이터 흐름이 바뀌면 서비스 문서 반영 여부를 확인한다.
- 큰 변경은 작은 작업 단위로 나눈다.

## 테스트와 검증 순서

코드 변경 후에는 최소한 아래를 확인한다.

1. 변경 범위에 가장 가까운 테스트
2. 관련 통합 테스트 또는 smoke test
3. formatter 또는 lint가 있는 경우 해당 명령
4. `git diff --check`
5. 실행 가능한 앱이면 로컬 실행 또는 브라우저 확인

테스트를 실행하지 못하면 완료 보고에 이유와 남은 리스크를 쓴다.

## Context 문서 반영 기준

이슈 해결 또는 PR 정리 전에는 `clever-context-monorepo` 반영 필요 여부를 확인한다.

- 서비스 책임, API, 데이터 흐름, public contract가 바뀌면 service 문서 반영을 검토한다.
- deploy profile, runtime, env/secret category가 바뀌면 service 문서와 deploy 기준 반영을 검토한다.
- 빠른 탐색 링크나 요약이 필요할 때만 `docs/wiki`를 수정한다.
- 문서 반영이 필요 없으면 이슈 또는 PR 정리에 불필요 사유를 남긴다.

## 완료 조건

작업 완료 전 아래를 확인한다.

- 연결된 issue와 branch가 맞다.
- 의도한 파일만 변경됐다.
- 필요한 테스트를 실행했다.
- context 문서 반영 필요 여부를 확인했다.
- 완료 보고에 변경 내용, 검증 결과, 다음 action을 남겼다.

## 금지 사항

- `AGENTS.md`를 프로젝트 기획서로 사용하지 않는다.
- `docs/project-brief.md`에 있어야 할 제품 설명을 이 파일에 길게 쓰지 않는다.
- `project-start issue #` 대신 임의의 change id를 root identifier로 쓰지 않는다.
- `dev`가 생긴 뒤 `main`에 직접 push하지 않는다.
- 사용자가 만들었을 수 있는 변경을 임의로 되돌리지 않는다.
