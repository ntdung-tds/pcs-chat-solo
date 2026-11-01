# PCS Chat Solo — AI quick entry (read this first)

**Purpose:** Deliver the user's project reliably. Do **not** read/clone the entire PCS repository into the chat context. This file is the default entrypoint; other files are consulted only when the task needs them.

## Standard resume command

**"Tiếp tục dự án theo PCS, sử dụng trạng thái mới nhất trên GitHub."** means resume the already identified project, using its latest verified GitHub state. First read the project's `pcs/MOMENT.md`, reconcile revision and GitHub HEAD with canonical `pcs/STATE.json`, then load only task-relevant changes, code, evidence and permissions. If multiple projects are plausible or no repository is known, ask only for the correct project URL. Do not assume GitHub access or pretend to persist changes when no write tool is available.

## Optional Skill

A single, short Skill is available in `.agents/skills/pcs-chat-solo/SKILL.md` for AI hosts that discover repository Skills. This does **not** install itself into ChatGPT or any other host. Prompt-first users can keep using this file without a Skill; do not create extra Skills for SRS changes, checklists or handoff.

## Start / resume
1. Read the user's request and available project sources. If the project exists, read its current `pcs/MOMENT.md` first, reconcile its revision with canonical `pcs/STATE.json`/HEAD using a bounded query where tools allow, then inspect only the relevant code, requirements and recent changes. If no PCS state exists, open `templates/STATE.example.json` **once** to initialize it.
2. Confirm actual tools, project repository and permissions. Never invent access, source contents, tests or deployments.
3. Plan a useful feature/flow, implement within authority, test realistically and show the Owner the result. High-risk work (production, permissions, secrets, deletion, restricted data) requires appropriate verified approval.
4. Checkpoint the single canonical `pcs/STATE.json`, derive `pcs/MOMENT.md`, verify persisted commit where connected, and report done/evidence/blockers/next action. If a remote write conflicts, reload and reconcile.

## Load further **only when needed**
- `docs/REQUIREMENT_CHANGE_CONTROL.md` — on active Task changes, automatically append delta to project `pcs/SRS_CHANGES.md`, without asking Owner for section number; never edit original SRS.
- `docs/CONTEXT_ENGINE.md` — on-demand context selection and cross-chat handoff; optional `tools/pcs_context.py`.
- `docs/WORKFLOW.md` — when planning a new/complex project, questions about workflow or acceptance.
- `docs/GITHUB_CONTINUITY.md` — when writing GitHub project state; repository visibility is **Owner-selected Public or Private**. For Public, verify all data/history is safe to publish and record explicit classification.
- `docs/STATE_OPERATIONS.md` — only for large backlogs, state inspection/diff, troubleshooting or sensitive-data handling.
- `templates/STATE.example.json` — only when creating state or checking its structure.
- `tools/pcs_solo.py` — only when using/debugging the optional local Python helper.
- `tests/`, `VERIFY_SEED.py`, `MANIFEST.sha256`, CI files — only when maintaining/testing PCS itself.
- `README.md`, `PROMPT.md` — for people choosing/starting PCS; an AI that has read this entrypoint need not re-read them.

A new chat resumes from **the project's latest verified state**, not by rereading all PCS documentation. Quality checks scale with task risk and impact; reducing unnecessary reads must never skip relevant evidence or safety checks.
