# issue resolution context wiki prompt

## 목적

이 문서는 target repo의 각 이슈 해결 시, 에이전트가 `clever-context-monorepo`의 service 문서와 wiki 반영 필요 여부를 같이 확인하도록 유도하는 복사용 프롬프트다.

이 프롬프트는 이슈 해결 완료 표시가 코드 변경 종료만으로 끝나지 않는다는 전제를 따른다.

즉 이슈 해결은 local 구현 결과가 global context에 남아야 하는지 확인하는 단위다.

## 사용 시점

아래 조건일 때 사용한다.

- target repo의 이슈를 해결 완료로 표시하기 전
- 이슈 종료 코멘트, PR 정리, merge 준비를 작성하기 전
- 변경 결과가 서비스 책임, public contract, deploy/runtime 기준, 운영 caveat에 영향을 줬는지 점검해야 할 때

## 프롬프트

```text
이번 작업은 이슈 해결 단위다.

해결 완료로 표시하기 전, 아래 기준으로 `clever-context-monorepo`의 context 문서 반영 필요 여부를 확인해줘.

1. 대상 이슈:
- issue:
- target repo:
- branch / commit / PR:
- 관련 service name이 있으면:

2. 반드시 확인할 것:
- `clever-context-monorepo/docs/services/<service>/index.md`
- 필요하면 `clever-context-monorepo/docs/wiki/`
- 필요하면 관련 `clever-context-monorepo/docs/root/` 또는 `contracts/`

3. 이 이슈에서 정리할 항목:
- 서비스가 실제로 하게 된 일 또는 책임 변화
- 주요 API / 기능 / 데이터 흐름 / public contract 변화
- deploy profile, runtime, env/secret category 변화
- template lineage 또는 service metadata 변화
- 운영상 새 caveat, 검증 증거, rollback 주의점
- wiki 탐색 링크나 요약 문서가 필요한지

4. 출력 방식:
- 먼저 context 문서 반영이 필요한지 판단
- 필요하면 수정 대상 파일을 `clever-context-monorepo` 경로로 제시
- service 문서가 정본이면 `docs/services/<service>/index.md`를 우선 수정
- docs/wiki는 정본이 아니다. 빠른 탐색이나 요약이 필요할 때만 수정
- 반영이 불필요하면 왜 불필요한지 이슈 종료 코멘트에 남길 문장으로 정리

기준:
- 이슈 해결은 context 반영 필요 여부를 확인하는 단위다.
- 서비스 정본은 service 문서에 둔다.
- wiki는 탐색 입구이며 최종 판단은 root, contracts, service 문서로 되돌아간다.
```

## 운영 규칙

- 모든 이슈 해결이 자동으로 wiki 수정으로 이어지지는 않는다.
- 하지만 에이전트는 매번 `업데이트 필요 여부`를 먼저 확인해야 한다.
- 서비스 범위 변경은 `clever-context-monorepo/docs/services/<service>/index.md`를 우선 수정한다.
- `docs/wiki/`는 탐색성이나 요약성이 필요한 경우에만 같이 수정한다.
- 이슈 종료 코멘트에는 context 문서 반영 여부 또는 불필요 사유를 남긴다.
