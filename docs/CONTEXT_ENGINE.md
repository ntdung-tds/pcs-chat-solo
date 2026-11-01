# PCS Chat Solo — Context-efficient continuation (3.3 candidate)

Keep the Solo project schema `pcs.solo.v1`, with one canonical `pcs/STATE.json` and derived `pcs/MOMENT.md`. This does **not** add contributors, Lead agents or another state store.

## Start, resume, handoff
1. Read `START_HERE.md` only once; on the next chat read the project's latest Moment and compare its revision to GitHub HEAD/canonical STATE.
2. Determine the active task and select relevant requirements, changed code, risks, test and evidence. Do not paste an entire backlog, old chat history, handbook or source tree into context.
3. Optional local Python: `python tools/pcs_context.py --file=/project/pcs/STATE.json --task=T1 --limit=6`. This reads and validates the whole state offline but returns bounded task metadata only. No Python install is required for ordinary chat use; connector-only sessions may need targeted reads instead.
4. Expand relevant details before decisions. High-risk permissions, public data, destructive changes and production require actual verified Owner approval. A short summary cannot substitute for source evidence, test logs, revision checks or authorization.
5. On completion, checkpoint under existing concurrency rules and give an explicit handoff: task ID, latest revision/commit, scope/files changed, test outcome and verified link, open risks, approval status, exact next action. If GitHub writes fail, state clearly that the handoff is not persisted.

## Token-aware verification
Compare baseline vs optimized input/output tokens when provider metrics exist, context spent before useful work, compaction count, recovery correctness and test outcomes. Do not invent metrics or claim measured savings from illustrative budgets. Caching lowers cost in some providers, not context occupancy. Never compress away current security gates or unverified blockers.
