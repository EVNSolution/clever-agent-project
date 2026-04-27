# CLEVER PR metadata

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

## Context/wiki upload metadata

- context docs checked:
  - `clever-context-monorepo/docs/services/<service>/index.md`
  - `clever-context-monorepo/docs/wiki/`
  - related `clever-context-monorepo/docs/root/` or `contracts/`
- context wiki upload status: `updated` / `not-needed`
- service doc update:
- wiki update:
- clever-context-monorepo commit/PR:
- not-needed reason:

## Linked issue close evidence

- linked issue close evidence:
- 이슈 종료는 이 PR metadata를 근거로 처리한다.
- 이슈 종료 코멘트에는 context/wiki 반영 결과 또는 불필요 사유를 이 PR에서 복사해 남긴다.

## PR 기준

- `dev` PR과 `main` PR은 이 metadata를 채운다.
- `main` PR은 deploy merge 단위로 보고 context/wiki 반영 여부를 다시 확인한다.
- `dev` PR은 integration merge 단위로 보고 issue close 전에 context/wiki 반영 여부를 묶어 확인한다.
