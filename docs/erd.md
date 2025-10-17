## Data Model & ERD

Entities: scenario (request/response snapshot), memo (rendered doc), audit_log.
Indexes: scenario.hash (idempotency), memo.scenario_id.

```mermaid
erDiagram
  SCENARIO {
    uuid id PK
    text hash UNIQUE
    json payload
    json result
    timestamptz created_at
  }
  MEMO {
    uuid id PK
    uuid scenario_id FK
    text html_url
    text pdf_url
    timestamptz created_at
  }
  AUDIT_LOG {
    uuid id PK
    text actor
    text action
    uuid scenario_id
    timestamptz created_at
  }
  SCENARIO ||--o{ MEMO : has
  SCENARIO ||--o{ AUDIT_LOG : logs
```

```
ASCII preview
SCENARIO(id, hash*, payload JSON, result JSON, created_at)
   ├── MEMO(id, scenario_id→SCENARIO.id, html_url, pdf_url, created_at)
   └── AUDIT_LOG(id, actor, action, scenario_id, created_at)
```

