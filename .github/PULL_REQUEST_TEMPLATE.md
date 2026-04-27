## change id

-

## 관련 issue

-

## 대상 repo/service

-

## 변경 내용

-

## PR Scope Grouping Gate

- grouping decision: `single-pr` / `split-required`
- same document/operating-rule cleanup:
- same validation command:
- different app/service/contract surface:
- merge order dependency:
- rollback unit:

같은 issue 안의 같은 운영 문서/절차 정리이고 같은 검증으로 충분하면 `single-pr`로 둔다.
앱, 서비스, 계약 표면, merge 순서, 롤백 단위가 다르면 `split-required`로 둔다.

## 테스트 여부

-

## 검수 포인트

-

## rollout/rollback 영향

-

## Concurrent Work Gate

- parallel work decision: `done` / `blocked` / `allowed-with-non-overlap` / `user-forced-proceed`
- target repo issue:
- clever-change-control issue:
- open PR checked:
- conflict candidates:
- user-forced-proceed reason:

## CLEVER PR review completion

- target branch: `dev` / `main`
- context docs checked:
- PR 정보를 wiki에 올리지 않는다.
- 검토 에이전트 작업은 wiki/service context 업데이트로 마친다.
- wiki/service context update result: `updated` / `not-needed`
- service doc update:
- wiki update:
- clever-context-monorepo update:
- linked issue close evidence:
