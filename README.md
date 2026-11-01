# PCS Chat Solo — One AI in a chat window

**Edition:** PCS Chat Solo 1.0.0. Designed for managing and continuing projects directly in ChatGPT, Claude, Gemini or another supported AI chat. No installer or dedicated runtime service is required.

## Đọc tài liệu theo nhu cầu (tiết kiệm context)

Khi AI bắt đầu, chỉ cần đọc [`START_HERE.md`](START_HERE.md) và **yêu cầu/trạng thái của repository dự án**. Không yêu cầu đọc toàn bộ `pcs-chat-solo`; `docs/WORKFLOW.md` mở khi lập kế hoạch phức tạp, mẫu STATE chỉ khi khởi tạo, còn `tools/`, `tests/` và CI chỉ khi trực tiếp phát triển hoặc kiểm thử PCS. Khi tiếp tục dự án, ưu tiên `pcs/MOMENT.md`, `pcs/STATE.json`, phần code và test vừa liên quan.

## Start

1. Open [`PROMPT.md`](PROMPT.md), copy the standard prompt into a chat with one AI.
2. Describe your idea or attach SRS/SOW; provide access to the project's GitHub repository when available.
3. The AI analyzes, plans, implements within its real available permissions, verifies, and checkpoints project state. A new chat resumes from the same project state.

The Project Owner reviews completed features, business flows and releases, while the AI manages planning, implementation, verification and project continuity.

## Separation and project storage

`pcs-chat-solo` is a **public package of instructions and optional validation tools**. It must never store an individual project's SRS, credentials, production data, screenshots containing secrets or user-private state.

Each real project has its own **private GitHub repository by default**, with a **single canonical** `pcs/STATE.json` and derived `pcs/MOMENT.md`. Under `pcs/moments/`, append immutable checkpoint records when tools permit. Project GitHub Issues are optional for meaningful tasks; Projects, Drive and PR are optional depending on real tools and risk. Don't invent connector access or test results.

## Continuity and approvals

- A single AI may span multiple chat sessions, but only **one active writer** at a time. Before changing state, reload `pcs/STATE.json` and verify its revision.
- A new chat/AI provider can **replace** the prior agent after handoff; this is not simultaneous collaboration.
- Use task states `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `TECH_DONE`, `INTEGRATION_PENDING`, `ACCEPTED`, `CANCELLED`. Mark `ACCEPTED` only with genuine evidence and authorized acceptance.
- A plain "OK" in the chat is useful product feedback, but does not grant GitHub privileges, approve production release, or cryptographically authenticate the Owner for privileged operations.
- Production, destructive actions, access rights, secrets and risky changes still require verified Owner authority and platform access controls.

## Optional local check for engineering users

No installation is needed for normal chat usage. If a coding environment with Python 3.10+ is available, it can validate/create/checkpoint a project state:

```bash
python tools/pcs_solo.py init --root /path/to/project --slug sample-project --name "Sample project"
python tools/pcs_solo.py verify --root /path/to/project
python tools/pcs_solo.py checkpoint --root /path/to/project --expect 1 --input /path/to/updated_state.json
```

The optional helper writes local files; it **does not** claim to upload them to GitHub. The agent must publish state using an authenticated GitHub connector and verify the commit, preferably in one commit with its Moment record. GitHub CAS/branch rules still govern concurrent remote writes.

## Product boundaries

- **PCS Desktop 2.1:** local coding-agent installer and legacy `pcs/current.json` format, not this repo.
- **PCS Multi-Agent 3.2:** `ntdung-tds/pcs-universal`, independent multi-agent edition.
- **PCS Chat Solo:** no agent registry, no required CLI, minimal source and tests.
