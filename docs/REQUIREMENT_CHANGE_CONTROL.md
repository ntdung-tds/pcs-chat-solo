# PCS SRS/đề cương changes — one-file active-task ledger (v2)

**Owner decision (binding):** During implementation, automatically capture **only deltas** from the original SRS/outline. Use the active PCS Task/Feature as context; **never require the Owner to know SRS section numbers or create CRs**. Keep the original SRS untouched. **Only after the entire project finishes** prepare a read-only comparison; SRS synchronization needs a separate explicit Owner decision and is optional.

## Project file and authority

New projects store the **sole new change history** in `pcs/SRS_CHANGES.md` inside the **project's repository**, not in the public PCS toolkit. Initialize it on the first real deviation:

```markdown
# PCS SRS Changes
<!-- pcs-srs-changes:v1 -->
```

`pcs/STATE.json` (Universal/Solo) or native `pcs/project.json` + `pcs/tasks.json` (Desktop) continues to own **project/task progress**. It is **not** a second requirement-change log. Do not copy the complete ledger into STATE/Moment. The older optional `requirement_changes[]` in state is **legacy-compatible read-only** for existing projects; do not dual-write or silently migrate it. An existing project with a populated legacy ledger requires explicit reconciliation before adopting the new file; an empty legacy array is not a reason to keep writing there.

The SRS baseline is read-only. A CR records task/feature context, `srs_ref` if it can be grounded, before/after text, reason, timestamp, and decision provenance. Only changes are recorded — not the complete SRS or large documents.

## Human workflow (no forms)

1. Owner says naturally e.g. "Mật khẩu chỉ cần 8 ký tự" while a Task is under way. Agent obtains **current active Task** from PCS state, links to a **unique** related Feature when known and checks the last effective change for that context. It compares the relevant baseline/code/acceptance criterion. The Agent creates `CR-...` automatically. The user never supplies `3.2`, a CR number or a file name.
2. If task links to multiple features, attach to the **Task** instead of guessing a Feature. If a SRS section cannot be proven, record `srs_ref: "UNMAPPED"` and resolve it later. If no valid active task exists, first identify the actual task; never invent context.
3. Append a `PROPOSE` event for each distinct delta, then a `DECIDE` event when genuinely decided (APPROVED/REJECTED). Never erase earlier proposals or decisions. A new proposal does **not** replace a previously approved change. A decision must reference its provenance; an ordinary chat direction can be marked as an **unverified working decision**, not as authenticated production/IAM/security approval. Sensitive changes always need verified authorization.
4. Every independent request gets its own generated CR ID as `item_key`, even when several changes affect the same Feature. When revising **the same** request, the Agent identifies its earlier CR and passes `revision_of`; the new revision retains the original `item_key`. Latest approved revision wins **within that chain only**. Unrelated changes never overwrite one another; conflicting approvals within one chain are blocked. Project QA and product acceptance are separate from a change decision.
5. On chat resume, load the current Task and only the short relevant change summary and any needed final delta. Fetch the whole history only for troubleshooting or end-of-project report. **Never automatically change the source SRS.**
6. Once the project is complete, generate **FOR OWNER DECISION — NOT APPLIED** change comparison, grouped by SRS reference, or by task/feature when still UNMAPPED. Do not create an SRS update PR or sync unless the Owner separately requests it.

## Append-only event format (one Markdown file)

Entries are a short Markdown heading followed by one JSON event in a `pcs-change` fenced block. The event store is machine-validatable, readable in GitHub and searchable by ID, without giant nested JSON blobs. The first event is e.g.:

```pcs-change
{"kind":"PROPOSE","id":"CR-1","task_id":"TASK-5","feature_id":"FEAT-2","item_key":"CR-1","srs_ref":"UNMAPPED","mapping":"ACTIVE_CONTEXT","ambiguous_features":false,"based_on":"BASELINE","before":"Tối thiểu 12 ký tự","after":"Tối thiểu 8 ký tự","reason":"Owner thay đổi khi đang làm task","at":"2026-11-01T10:00:00Z"}
```

A revision is a new `PROPOSE` with `revision_of` pointing to a prior CR of the same requirement. The helper retains the original `item_key`. A decision is another event with the **same CR ID**: `{"kind":"DECIDE","id":"CR-1","decision":"APPROVED","actor":"owner","ref":"source-of-decision","at":"2026-11-01T10:01:00Z"}`. The decision record alone is not external verification. Do not fabricate refs.

## Agent tools and token limits

- Universal/Desktop (optional Node): `tools/pcs-srs-changes.mjs`
- Chat Solo (optional Python): `tools/pcs_srs_changes.py`
- Read active change only: `node tools/pcs-srs-changes.mjs --root=/project --item=TASK-5` (Solo: `python tools/pcs_srs_changes.py --root=/project --item=TASK-5`).
- For recording, an Agent creates a small local JSON event request and calls `--record=/tmp/change.json --root=/project`; a `PROPOSE` request can omit task/feature/section because the helper derives them from current PCS state (Desktop also needs `--desktop=true`). An explicit `DECIDE` references the CR.
- If the Agent works through a GitHub connector rather than CLI, it can append the same format, but must read current blob SHA/revision, validate before updating, use GitHub conditional updates/PR controls and re-read commit. **Do not assume the optional local lock serializes separate GitHub Agents.**
- Summary output is **bounded to 10 change groups by default** (at most 20); `total_items` and `next_offset` allow pagination (`--offset=10`, `--max-items=10`). Filtering by `--item=TASK-5` or a Feature ID finds related independent changes; the Owner does not need to know CR IDs. Each group returns only its effective delta, counts and a few recent IDs. Large local file parsing does not require pasting the entire ledger into the model context. On connectors that expose only whole files, consider a future selective index/splitting **after measurement**, not as the default.
- Initial single-file strategy is deliberately simple. If concurrent writes or file size measurably cause problems, shard by item later behind the same interface. This is **not** automatic today.

**Security / limits:** Enforce repository data classification and access, do not write restricted information in public repos. `verified_external_decision:false` is deliberate; external identity, link, SHA, SRS section mapping and real deployment/tests require independent checks. No new state schema, no changes to the locked Desktop distribution, no automatic migration or SRS sync.
