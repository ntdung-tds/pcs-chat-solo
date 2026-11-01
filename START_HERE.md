# PCS Chat Solo 1.0 — AI entrypoint

1. Read [`docs/WORKFLOW.md`](docs/WORKFLOW.md), inspect the user's SRS/repository and identify available tools before claiming any action.
2. Read the current private project `pcs/STATE.json` (or initialize from [`templates/STATE.example.json`](templates/STATE.example.json)). Validate the owner-owned project reference and maintain its revision; `pcs/MOMENT.md` is a rendered view, not a second source of truth.
3. Plan and carry out project tasks with the available tools. The Project Owner reviews meaningful product outcomes and provides feedback.
4. Plan business flows → features → tasks; choose smallest meaningful unit, maintain dependencies and evidence/QA. Work autonomously on low-risk tasks. Use `BLOCKED` for unresolved permissions/requirements. Leave high-risk operations to Owner approval verified through an appropriate authority channel.
5. Work only with genuinely available tools. For GitHub writes, verify branch/revision/commit and use PRs or compare-and-swap where required; do not overwrite concurrent writes even though Solo assumes one active AI. Do not claim unobserved deployment/tests.
6. At completion, update `pcs/STATE.json` and derived Moment, persist externally if authorized, and provide the product for Owner review. A next chat must resume from verified state, not pretend persistent local context.

Use the PCS Chat Solo project-state format for continuity, and migrate other PCS formats only through an explicit, verified migration.
