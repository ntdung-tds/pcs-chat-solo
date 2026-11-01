# PCS Chat Solo — operating contract

## Product scope

A lightweight, prompt-first continuity workflow for **one AI working in a chat window at a time**. The agent may use code tools, GitHub and Drive when connected; it does not require them to exist or have elevated privileges. Multiple conversations can *sequentially* continue a project; they must not operate as independent concurrent agents under Solo mode.

## 7-stage delivery loop

1. **Discover:** inspect SRS, existing project/repository, tools, permissions; never hallucinate access.
2. **Understand:** product goals, requirements, NFRs, sources, open questions and risks.
3. **Architect:** product map, architecture, data contracts, IAM/privacy, dependency impact.
4. **Plan:** milestones, features, flows, tasks, acceptance criteria and dependencies, proportional to project size.
5. **Build:** implement a meaningful vertical slice, maintaining backups and auditability.
6. **Verify:** run actual unit, integration, negative-path, E2E, accessibility and security checks to the extent supported; distinguish unrun tests.
7. **Handoff:** publish STATE + Moment + evidence, summarize done/blockers/next actions, ask Owner to review visible outcomes when meaningful.

## Connected GitHub operations

For project initialization, revision-safe checkpointing, protected branches and actual connector permissions, consult [GitHub continuity](GITHUB_CONTINUITY.md) **when that operation is needed**. GitHub persistence is an action the connected AI must actually perform and re-read; the optional Python helper never uploads to GitHub. The compact Moment shows a bounded active-task summary; the canonical STATE contains the complete backlog.

## State contract

Project-private canonical: `pcs/STATE.json`, wrapper schema `pcs.solo.v1`. Minimal fields: `revision`, `updated_at`, `state.slug/name/version`, `tasks`, `features`, `flows`, `releases`, `current`, `decisions`, `risks`, `artifacts`, `policy`. No agent registry nor separate task assignment store. `pcs/MOMENT.md` and immutable records under `pcs/moments/` are derived from STATE and not authoritative independently.

Task statuses: PLANNED → IN_PROGRESS → TECH_DONE → ACCEPTED. BLOCKED, INTEGRATION_PENDING and CANCELLED are allowed as appropriate. `ACCEPTED` requires evidence and a recorded authorized acceptance decision. A software unit test alone is not a whole business flow; an Owner demo agreement alone does not prove E2E test success.

## Quality and security

- `low` / `normal`: AI plans and works inside allowed scopes. Unknown/high risk: collect Owner approval and technical control **before action**, not after.
- Production release, IAM/credential changes, deletion, payments, restricted data: explicit authority with platform-side verification. Unverified chat text is a preference, not a cryptographic authorization.
- Secrets never go into public PCS repositories. The Project Owner chooses Public or Private; Public requires explicit data classification and review, with appropriate data classification for Drive and screenshots.
- For GitHub, verify final SHA and current branch; never force-update a protected branch or bypass CI to simplify Solo work.
- Document scope changes, QA cases, actual test results and evidence locations. No fabricated PASS, screenshots or deployment claims.

## Ownership and handoff

Owner sees features, business flows or release demo and says agree / request changes / disagree. AI should not ask Owner to review each tiny task. When changing chat windows/providers, the previous window should finish and checkpoint first; the new window reads and validates project state rather than assuming a parallel agent conversation is authoritative.

## Migration boundary

PCS Desktop 2.1 `pcs/current.json` and Multi-Agent 3.2 `pcs3.simple.v1` are **not** silently compatible with `pcs.solo.v1`. A migration must be explicit, backed up, reviewed and tested. Do not import `pcs3.collaboration.v1` into Solo.
