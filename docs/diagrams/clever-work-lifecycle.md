# 세션 시작부터 대상 레포지토리 실행까지

저장소 화면에서 바로 읽는 용도의 실행 흐름도다. 각 단계마다 어떤 레포와 디렉터리/파일이 관여하는지 같이 본다.

```mermaid
sequenceDiagram
    actor U as 사용자
    participant AP as clever-agent-project
    participant CTX as clever-context-monorepo
    participant CC as clever-change-control
    participant TR as 대상 레포지토리

    U->>AP: 세션 시작<br/>README.md
    AP->>U: 쉬운 시작 템플릿 제시<br/>README.md + SKILL.md
    U->>AP: 작업 성격 + 대상 범위 + 목표 수준 입력

    AP->>AP: 요청 정규화<br/>docs/setting.md + guides
    AP->>CTX: 권한과 계보 해석<br/>docs/root/index.md<br/>authority-boundaries.md
    CTX-->>AP: 루트 규칙 + 후보 템플릿 계보 반환
    AP->>CTX: 필요 시 서비스 메타데이터 조회<br/>docs/services/service-*/index.md
    CTX-->>AP: 배포 프로파일 + 기존 계보 반환

    AP->>AP: bootstrap packet 생성<br/>bootstrap_clever_work.py
    AP-->>U: project-start payload 초안 제시<br/>후보 레포/service + 계보
    U->>AP: 초안 승인

    AP->>CC: 루트 line 생성<br/>project-start template + README rules
    CC-->>AP: 루트 기준 식별자 = project-start issue #

    AP->>CTX: 범위가 좁혀진 서비스 문맥 재확인
    CTX-->>AP: target service와 서비스별 메타데이터 확인

    AP->>CC: 범위가 고정된 실행으로 전환<br/>change request + changes/ + releases/
    CC-->>AP: 범위 확정<br/>repo + service + change_id

    AP->>TR: 구현 레포로 넘김
    TR->>TR: 구현 + 테스트 + 빌드
    TR-->>CC: PR + 배포/롤백 증적 연결
```

## 단계 요약

1. 시작은 `clever-agent-project/README.md`에서 열린다.
2. 하드 게이트는 `SKILL.md`와 시작 템플릿 규칙으로 강제되고, 답변은 `work_nature`, `target_scope`, `goal_level` 중심으로 정규화된다.
3. 해석은 `clever-context-monorepo/docs/root`, `docs/services`, `docs/templates`를 읽어 결정한다.
4. 루트는 `clever-change-control`의 `project-start issue #`로 열린다.
5. 범위가 고정된 실행은 `change request`, `changes/`, `releases/*`로 내려간다.
6. 구현은 대상 레포지토리에서 하고, 증적만 다시 change-control로 연결한다.
