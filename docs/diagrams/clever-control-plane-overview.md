# 3레포 제어 평면 개요

저장소 화면에서 바로 읽는 용도의 구조도다. `clever-agent-project`가 시작점을 열고, `clever-context-monorepo`가 해석 정본을 제공하고, `clever-change-control`이 루트와 범위 추적을 남긴 뒤, 실제 구현은 대상 레포지토리로 넘어간다.

```mermaid
flowchart LR
    user["사용자 세션"]

    subgraph AP["clever-agent-project"]
        ap_readme["README.md<br/>세션 시작 템플릿"]
        ap_skill[".agent/skills/bootstrap-clever-work/<br/>SKILL.md + bootstrap_clever_work.py"]
        ap_docs["docs/<br/>setting.md · guides · diagrams"]
        ap_runtime["scripts/ + tests/<br/>bootstrap 진입점 + 검증"]
    end

    subgraph CTX["clever-context-monorepo"]
        ctx_root["docs/root/<br/>권한 경계 · 런타임 규칙 · 파이프라인 규칙"]
        ctx_services["docs/services/<br/>service-template + service-*/index.md"]
        ctx_templates["docs/templates/<br/>템플릿 레지스트리 + 계보"]
        ctx_support["templates/deploy/ + contracts + wiki<br/>배포 골격 + 참조 앵커"]
    end

    subgraph CC["clever-change-control"]
        cc_readme["README.md<br/>루트 식별자 + change_id 규칙"]
        cc_issue[".github/ISSUE_TEMPLATE/<br/>project-start · 변경 요청 · 롤백"]
        cc_changes["changes/<br/>범위가 고정된 변경 anchor"]
        cc_releases["releases/dev · stg · prod<br/>릴리스 증적"]
    end

    subgraph TR["대상 레포지토리"]
        tr_code["src/ 또는 app/<br/>실제 구현"]
        tr_tests["tests/ + CI/deploy config<br/>검증 + 빌드"]
        tr_docs["docs/specs if needed<br/>로컬 구현 문맥"]
    end

    user --> ap_readme
    ap_readme --> ap_skill
    ap_skill --> ap_docs
    ap_skill --> ctx_root
    ap_skill --> ctx_templates
    ap_docs --> ctx_services
    ctx_root --> ctx_services
    ctx_templates --> ctx_support
    ap_skill --> cc_readme
    ap_skill --> cc_issue
    cc_issue --> cc_changes
    cc_changes --> cc_releases
    ctx_services -. 규칙 + 계보 .-> tr_code
    cc_changes --> tr_code
    tr_code --> tr_tests
    tr_tests --> tr_docs
    tr_tests -. 증적 환류 .-> cc_releases
```

## 읽는 법

- `clever-agent-project`는 사용자 요청을 intake하고 bootstrap packet을 만든다.
- `clever-context-monorepo`는 루트 규칙, 서비스 메타데이터, 템플릿 계보를 해석한다.
- `clever-change-control`은 `project-start issue #`와 범위가 고정된 변경을 기록한다.
- 실제 코드와 검증은 대상 레포지토리에서만 수행된다.
