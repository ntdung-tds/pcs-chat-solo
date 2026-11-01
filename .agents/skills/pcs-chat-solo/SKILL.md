---
name: pcs-chat-solo
description: Use for starting, resuming, handing off, or revising requirements in a PCS Chat Solo project; especially when asked to "tiếp tục dự án theo PCS" using latest GitHub state.
---

# PCS Chat Solo — optional portable Skill

This is **one optional Skill**, not a plugin or extra PCS runtime. It may be used as a standalone installed Skill; the full toolkit is not assumed to be in the current working directory. Without Skill installation the standard prompt-first workflow still works.

1. **Resume:** Identify the user's actual project repo, read its latest `pcs/MOMENT.md`, reconcile `pcs/STATE.json` revision with GitHub HEAD and inspect only the active Task/Feature, relevant code and actual evidence. If the repo is unknown, request its link only. With no GitHub write access, explicitly report local or blocked persistence.
2. **Work and verify:** Follow the project task, write and test only with real tools/permissions; preserve branch/PR rules and Owner acceptance gates. A chat "OK" never impersonates verified high-risk approval. Don't mark unrun tests or unsaved checkpoints as complete.
3. **SRS deviations:** When requirements change during an active Task, automatically identify Task/Feature. Log **only the delta** and decision trail in the **project's** `pcs/SRS_CHANGES.md` (not STATE); mark unverified SRS sections `UNMAPPED`. New proposals do not override approved changes. Never alter source SRS/outline until the entire project is complete and the Owner separately requests synchronization.
4. **Handoff:** Verify the saved state/Moment when connected, and report the task, evidence, blockers and exactly one next step. Use the smallest relevant context.

**Optional on-demand toolkit references:** [PCS Solo entrypoint](https://github.com/ntdung-tds/pcs-chat-solo/blob/main/START_HERE.md), [change ledger format](https://github.com/ntdung-tds/pcs-chat-solo/blob/main/docs/REQUIREMENT_CHANGE_CONTROL.md), [context rules](https://github.com/ntdung-tds/pcs-chat-solo/blob/main/docs/CONTEXT_ENGINE.md). Access these only when necessary and supported; do not claim the file exists inside a different project.

**Not for:** unrelated chat questions, projects not using PCS, or simultaneous multi-agent orchestration (use Multi-Agent instead).
