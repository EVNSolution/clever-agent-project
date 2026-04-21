# 3레포 책임 분담도

디렉터리 트리를 그대로 보여주기보다, 각 책임이 어느 레포에 놓여 있는지를 빠르게 읽기 위한 다이어그램이다. 메인 README에는 이 다이어그램을 우선 노출하고, 상세 트리는 별도 문서로 분리한다.

```mermaid
flowchart TB
    start["시작 / 요청 접수 / 시작 패킷"]
    interpret["정본 해석 / 템플릿 계보 / 서비스 메타데이터"]
    approve["루트 열기 / project-start"]
    scope["범위 확정 / change request / change_id"]
    implement["구현 / 테스트 / 빌드"]
    evidence["배포 증적 / 롤백 추적 / 릴리스 기록"]

    ap["clever-agent-project<br/>README.md · SKILL.md · scripts"]
    ctx["clever-context-monorepo<br/>docs/root · docs/services · docs/templates"]
    cc_root["clever-change-control<br/>README.md · ISSUE_TEMPLATE"]
    cc_scope["clever-change-control<br/>changes · releases"]
    tr["대상 레포지토리<br/>src/app · tests · CI/deploy"]

    start --> ap
    interpret --> ctx
    approve --> cc_root
    scope --> cc_scope
    implement --> tr
    evidence --> cc_scope

    ap -. 해석 요청 .-> ctx
    ap -. 루트 연결 .-> cc_root
    cc_scope -. 구현 handoff .-> tr
    tr -. 증적 환류 .-> cc_scope
```

## 읽는 법

- 시작과 요청 접수는 `clever-agent-project`가 맡는다.
- 규칙, 템플릿 계보, 서비스 문맥 해석은 `clever-context-monorepo`가 맡는다.
- `project-start` 루트와 범위가 고정된 변경 추적은 `clever-change-control`이 맡는다.
- 실제 코드 변경과 테스트는 대상 레포지토리에서 수행한다.
- 배포 증적과 롤백 추적은 다시 `clever-change-control`로 환류된다.
