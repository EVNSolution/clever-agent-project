# Three-Repo Control Plane Overview

저장소 화면에서 바로 읽는 용도의 구조도다. `clever-agent-project`가 시작점을 열고, `clever-context-monorepo`가 해석 정본을 제공하고, `clever-change-control`이 root/scoped trace를 남긴 뒤, 실제 구현은 target repo로 넘어간다.

```mermaid
flowchart LR
    user["User session"]

    subgraph AP["clever-agent-project"]
        ap_readme["README.md<br/>세션 시작 템플릿"]
        ap_skill[".agent/skills/bootstrap-clever-work/<br/>SKILL.md + bootstrap_clever_work.py"]
        ap_docs["docs/<br/>setting.md · guides · diagrams"]
        ap_runtime["scripts/ + tests/<br/>bootstrap entry + verification"]
    end

    subgraph CTX["clever-context-monorepo"]
        ctx_root["docs/root/<br/>authority-boundaries · runtime governance · pipeline rules"]
        ctx_services["docs/services/<br/>service-template + service-*/index.md"]
        ctx_templates["docs/templates/<br/>template registry + lineage"]
        ctx_support["templates/deploy/ + contracts + wiki<br/>deploy skeleton + reference anchors"]
    end

    subgraph CC["clever-change-control"]
        cc_readme["README.md<br/>root id + change_id rules"]
        cc_issue[".github/ISSUE_TEMPLATE/<br/>project-start · change request · rollback"]
        cc_changes["changes/<br/>scoped change anchors"]
        cc_releases["releases/dev · stg · prod<br/>release evidence"]
    end

    subgraph TR["target repo"]
        tr_code["src/ or app/<br/>implementation"]
        tr_tests["tests/ + CI/deploy config<br/>verification + build"]
        tr_docs["docs/specs if needed<br/>local implementation context"]
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
    ctx_services -. rules + lineage .-> tr_code
    cc_changes --> tr_code
    tr_code --> tr_tests
    tr_tests --> tr_docs
    tr_tests -. evidence back .-> cc_releases
```

## 읽는 법

- `clever-agent-project`는 사용자 요청을 intake하고 bootstrap packet을 만든다.
- `clever-context-monorepo`는 root rules, service metadata, template lineage를 해석한다.
- `clever-change-control`은 `project-start issue #`와 scoped change를 기록한다.
- 실제 코드와 검증은 target repo에서만 수행된다.
