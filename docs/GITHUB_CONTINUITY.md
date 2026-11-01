# GitHub continuity contract — PCS Chat Solo

Read **only when** working with GitHub project state, creating a project repository or troubleshooting a checkpoint. This document describes connector operations, not a built-in GitHub sync client.

## Role of GitHub

- The public `pcs-chat-solo` repository provides PCS instructions and optional local validation tools. **Never save a user's project or secrets here.**
- Each project uses its own repository, **Public or Private as selected by the Owner**, subject to its classification and Owner permissions.
- One authoritative `pcs/STATE.json` (`schema: pcs.solo.v1`), a short derived `pcs/MOMENT.md`, optional immutable `pcs/moments/MOM-...json`. GitHub Issues/PRs are evidence and coordination, not a second source of truth.
- The connected AI must inspect its **real** permissions before acting. The local Python helper writes only local files; GitHub persistence requires an authenticated connector or authorized environment.

## First project

1. Discover an existing project repo before creating another; do not overwrite an unrelated repo. Verify owner/repository/visibility with the provider. If none exists and creation isn't available, ask for the single needed repository setup or permission; avoid claiming persistence.
2. Read the user's sources and current code if adopting; preserve the existing branch and working files. For new projects, initialize the example `pcs/STATE.json` with the actual slug/name and ISO timestamp; generate `pcs/MOMENT.md` from the same revision. Never copy example values as facts.
3. Record a minimal project map, requirements/assumptions, meaningful feature/flow backlog, acceptance tests and next step **in the project repository**. Create additional design/QA documents only when the project warrants them.

## Resuming and saving a checkpoint

1. **Read first:** repository identity/visibility, default branch HEAD SHA, current `pcs/STATE.json` and its `revision`; read short Moment to navigate, but STATE remains authoritative. Check relevant code, PRs, CI and recent commits before deciding what changed.
2. **Prepare:** increment revision exactly once, preserve project identity, include actual evidence links and next step, derive Moment from that new STATE. Validate the new state when an available validator permits. Do not mark tests/Owner approval VERIFIED merely by writing that word.
3. **Prefer one commit:** use provider Git Data equivalents to create blobs for `pcs/STATE.json`, `pcs/MOMENT.md` and optional snapshot; create **one tree** based on the observed HEAD tree, then one commit with the **observed HEAD as parent**. Update the branch only if that commit is a fast-forward from its current head (and use an expected-head/lease check when the connector supports one). Do not force-push.
4. **Confirm:** re-read the branch HEAD and both files. Report checkpoint success only after the expected commit is reachable and the new STATE revision and Moment agree. If ref update conflicts, reload and reconcile; an orphaned unreferenced commit is **not** a saved checkpoint.
5. **Protected branch:** if writes are rejected, use a permitted branch + PR and mark `REVIEW_REQUIRED` until merged and verified; never claim that an open PR already changed the canonical project state.
6. **Only single-file writes supported?** No atomic multi-file guarantee. Write to a working branch / PR if possible. If a partial write is unavoidable, explicitly report `PERSISTENCE_INCOMPLETE` and do not regard the project checkpoint as complete until both STATE and Moment are consistent and verified. Never silently overwrite newer revisions.

## GitHub Issues, test results and Owner review

- Create GitHub Issues for meaningful work units when useful, not one issue per trivial substep. Search task ID/marker first to avoid duplicate Issues; keep task IDs linked to actual evidence.
- Code changes follow repository PR/branch/CI policy. PR merged or Issue closed is **not** acceptance. Real test tool results must support claimed PASS, integration and E2E. The STATE's `verified: true` flag is only a **structural assertion** until its linked source and authority are independently inspected.
- Routine product feedback from chat may guide revisions; production, IAM, secrets, deletion, external spend and release approvals require appropriate authenticated Owner authority and platform permissions.

## Connection and limits

The agent may use the GitHub connector already supported in its chat platform. GitHub login/installation, repository permissions, branch protection and tool availability vary by platform. This repository **does not ship a GitHub App, cloud runner, background monitor or live GitHub E2E-certified client**. It provides a workflow for an AI to execute using real tools. If read/write access is unavailable, state precisely `PERSISTENCE_BLOCKED`, provide a portable checkpoint and avoid claiming GitHub synchronization. Tests in this repository are local/mock validation, not proof of cross-provider GitHub operations.
