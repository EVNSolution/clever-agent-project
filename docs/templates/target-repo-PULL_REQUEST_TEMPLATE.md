# CLEVER PR review completion

- target repo: `<target_repo>`
- target service: `<target_service>`
- target branch: `dev` / `main`
- source branch:
- project-start issue:
- change-control issue:
- target repo issue:

## 변경 내용

-

## 검증

-

## Concurrent Work Gate

- parallel work decision: `done` / `blocked` / `allowed-with-non-overlap` / `user-forced-proceed`
- target repo issue:
- clever-change-control issue:
- open PR checked:
- conflict candidates:
- user-forced-proceed reason:

## PR 검토 에이전트 종료 조건

- 검토 에이전트 작업은 wiki/service context 업데이트로 마친다.
- PR 정보를 wiki에 올리지 않는다.
- wiki에는 필요한 서비스 책임, public contract, deploy/runtime 기준, 운영 caveat, 빠른 탐색 요약만 반영한다.

## Context/wiki completion

- context docs checked:
  - `clever-context-monorepo/docs/services/<service>/index.md`
  - `clever-context-monorepo/docs/wiki/`
  - related `clever-context-monorepo/docs/root/` or `contracts/`
- wiki/service context update result: `updated` / `not-needed`
- service doc update:
- wiki update:
- clever-context-monorepo update:
- not-needed reason:

## Linked issue close evidence

- linked issue close evidence:
- 이슈 종료는 PR 검토 완료 결과를 근거로 처리한다.
- 이슈 종료 코멘트에는 wiki/service context 반영 결과 또는 불필요 사유를 이 PR에서 복사해 남긴다.

## PR 완료 후 branch 정리

- PR merge 후 source branch에 open PR, 후속 issue, child branch, active release/hotfix가 없으면 정리한다.
- `main`과 `dev`는 삭제 대상이 아니다.
- cleanup commands:

```bash
git switch dev
git pull --ff-only origin dev
git branch -d <source-branch>
git push origin --delete <source-branch>
git fetch --prune origin
```

## PR 기준

- `dev` PR과 `main` PR은 검토 에이전트 종료 조건을 채운다.
- `main` PR은 deploy merge 단위로 보고 wiki/service context 업데이트 여부를 다시 확인한다.
- `dev` PR은 integration merge 단위로 보고 issue close 전에 wiki/service context 업데이트 여부를 확인한다.
