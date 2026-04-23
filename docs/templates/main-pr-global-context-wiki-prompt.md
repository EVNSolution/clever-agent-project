# main PR global context wiki prompt

## 목적

이 문서는 `main`으로 머지되는 PR 단위에서, 에이전트가 글로벌 컨텍스트 wiki와 서비스 문서를 같이 정리하도록 유도하는 복사용 프롬프트다.

이 프롬프트는 `main`이 deploy branch라는 전제를 따른다.

즉 `main` merge는 코드 merge만이 아니라, global context 반영 단위이기도 하다.

## 사용 시점

아래 조건일 때 사용한다.

- target repo에서 `main`으로 들어갈 PR merge를 준비할 때
- 배포 단위로 간주되는 변경을 정리할 때
- 서비스 문서나 글로벌 탐색 문서 업데이트가 필요한지 같이 점검해야 할 때

## 프롬프트

```text
이번 작업은 `main` merge 단위다.

아래 기준으로 `clever-context-monorepo`의 글로벌 컨텍스트를 같이 정리해줘.

1. 대상 서비스:
- service name:
- target repo:
- related PR / merge unit:

2. 반드시 확인할 것:
- `clever-context-monorepo/docs/services/<service>/index.md`
- 필요하면 `clever-context-monorepo/docs/wiki/index.md`
- 필요하면 관련 `docs/wiki/*` 문서

3. 이번 merge에서 정리할 항목:
- 서비스가 실제로 무엇을 하게 되었는지
- 주요 API / 기능 / 책임 변화
- template lineage 변화 여부
- deploy profile 변화 여부
- env/secret category 변화 여부
- public contract 또는 probe 관점의 변화
- 운영상 새 caveat 또는 주의점

4. 출력 방식:
- 먼저 현재 서비스 문서와 wiki에 반영해야 할 변경점을 요약
- 그다음 실제 수정이 필요한 파일 목록 제시
- 가능하면 바로 문서 수정까지 진행
- 문서 반영이 불필요하면 왜 불필요한지 명확히 설명

기준:
- `main = deploy`
- `dev = work`
- `branch = 역할별 작업`
- `main` merge는 글로벌 컨텍스트 반영 단위로 본다.
```

## 운영 규칙

- 모든 `main` merge가 자동으로 wiki 수정으로 이어지지는 않는다.
- 하지만 에이전트는 매번 `업데이트 필요 여부`를 먼저 확인해야 한다.
- 서비스 문서가 더 적절한 정본이면 `docs/services/<service>/index.md`를 우선 수정한다.
- `docs/wiki/`는 탐색성과 요약성이 필요할 때만 같이 손댄다.
