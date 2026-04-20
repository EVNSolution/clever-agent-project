# Session Start To Target-Repo Execution

저장소 화면에서 바로 읽는 용도의 실행 흐름도다. 각 단계마다 어떤 레포와 디렉터리/파일이 관여하는지 같이 본다.

```mermaid
sequenceDiagram
    actor U as User
    participant AP as clever-agent-project
    participant CTX as clever-context-monorepo
    participant CC as clever-change-control
    participant TR as target repo

    U->>AP: Open session<br/>README.md
    AP->>U: Enforce 3-step start template<br/>README.md + SKILL.md
    U->>AP: Fill work type + MSA/MONO + extra context

    AP->>AP: Normalize request<br/>docs/setting.md + guides
    AP->>CTX: Read authority and lineage<br/>docs/root/index.md<br/>authority-boundaries.md
    CTX-->>AP: Return root rules + candidate template lineage
    AP->>CTX: Read service metadata if needed<br/>docs/services/service-*/index.md
    CTX-->>AP: Return deploy profile + existing lineage

    AP->>AP: Build bootstrap packet<br/>bootstrap_clever_work.py
    AP-->>U: Draft project-start payload<br/>candidate repo/service + lineage
    U->>AP: Approve draft

    AP->>CC: Open root line<br/>project-start template + README rules
    CC-->>AP: Root canonical identifier = project-start issue #

    AP->>CTX: Re-read only scoped service context
    CTX-->>AP: Confirm target service and service-specific metadata

    AP->>CC: Drop into scoped execution<br/>change request + changes/ + releases/
    CC-->>AP: Scope fixed<br/>repo + service + change_id

    AP->>TR: Handoff to implementation repo
    TR->>TR: Implement + test + build
    TR-->>CC: Link PR + rollout/rollback evidence
```

## 단계 요약

1. 시작은 `clever-agent-project/README.md`에서 열린다.
2. 하드 게이트는 `SKILL.md`와 시작 템플릿 규칙으로 강제된다.
3. 해석은 `clever-context-monorepo/docs/root`, `docs/services`, `docs/templates`를 읽어 결정한다.
4. root는 `clever-change-control`의 `project-start issue #`로 열린다.
5. scoped execution은 `change request`, `changes/`, `releases/*`로 내려간다.
6. 구현은 target repo에서 하고, 증적만 다시 change-control로 연결한다.
