---
name: pcs-chat-solo
description: Use to start, resume or hand off a PCS Chat Solo project, or record changes to its requirements during an active task; load only needed GitHub context.
---

# PCS Chat Solo — optional Skill

This Skill is **not required**. The user can use `PROMPT.md` and `START_HERE.md` directly, without installing a plugin, Skill or CLI.

1. Read `START_HERE.md` for the minimal workflow. This public toolkit does not hold the user's project files.
2. Resume from the **project's** latest `pcs/MOMENT.md`; reconcile `pcs/STATE.json` revision and GitHub HEAD before writing. Inspect only active Task/Feature, affected code and real evidence. If GitHub is unavailable, say so.
3. If requirements change during a task, identify that Task/Feature from existing PCS state. Record the short delta and decision history in **project** `pcs/SRS_CHANGES.md` as specified by `docs/REQUIREMENT_CHANGE_CONTROL.md`. The Owner does not need to know a section number; use `UNMAPPED` rather than guessing. A pending proposal does not override the last approved change. **Do not update the original SRS/outline** until the entire project is complete and the Owner separately authorizes it.
4. Implement/test within real permissions; checkpoint state and Moment only with verified evidence. Respect risks, PR rules and explicit high-risk approval. Report what was done, what was not verified and the next action.

Open `docs/CONTEXT_ENGINE.md`, `docs/WORKFLOW.md` or security guides **only when that task needs them**. Do not read all toolkits, archives or logs into the model context.
