# PCS SRS/đề cương changes — one-file active-task ledger (v2)

**Owner decision (binding):** During implementation, automatically capture **only deltas** from the original SRS/outline. Use the active PCS Task/Feature as context; **never require the Owner to know SRS section numbers or create CRs**. Keep the original SRS untouched. **Only after the entire project finishes** prepare a read-only comparison; SRS synchronization needs a separate explicit Owner decision and is optional.

## Project file and authority

New projects store the **sole new change history** in `pcs/SRS_CHANGES.md` inside the **project's repository**, not in the public PCS toolkit. Initialize it on the first real deviation:

```markdown
# PCS SRS Changes
<!-- pcs-srs-changes:v1 -->
```

`pcs/STATE.json` (Universal/Solo) or native `pcs/project.json` + `pcs/tasks.json` (Desktop) continues to own **project/task progress**. It is **not** a second requirement-change log. Do not copy the complete ledger into STATE/Moment. The older optional `requirement_changes[]` in state is **legacy-compatible read-only** for existing projects; do not dual-write or silently migrate it. An existing project with a populated legacy ledger requires explicit reconciliation before adopting the new file; an empty legacy array is not a reason to keep writing there.

The SRS baseline is read-only. Each CR records Task/Feature context, **one specific criterion** (`requirement_key`, a short stable slug inferred by the Agent), an SRS reference if verified, before/after wording, reason, timestamp and decision evidence. The Feature ID alone cannot identify a requirement: password length and username length must have separate chains.

## Human workflow (no forms)

1. Owner speaks naturally (for example, "Mật khẩu chỉ cần 8 ký tự") during an active Task. Agent reads that Task and uniquely related Feature, identifies **which criterion** changed, and generates a stable key such as `password-length` itself. It compares the last effective wording and source evidence; user never supplies an SRS section, CR ID, requirement key or filename. If uncertain which criterion is intended, do not mark a change approved or map it to an unrelated requirement.
2. If a Task relates to several Features, use the Task context rather than guessing. Independently changed requirements within that Task or Feature need distinct stable `requirement_key` slugs; the next delta for an approved criterion must start from the previous approved `after` wording. If its exact SRS section is unknown, set `srs_ref: "UNMAPPED"`, and reconcile later. Never invent an active task or SRS section.
3. Append a `PROPOSE` event for each distinct delta, then a `DECIDE` event when genuinely decided (APPROVED/REJECTED). Never erase earlier proposals or decisions. A new proposal does **not** replace a previously approved change. A decision must reference its provenance; an ordinary chat direction can be marked as an **unverified working decision**, not as authenticated production/IAM/security approval. Sensitive changes always need verified authorization.
4. The **latest approved change in a non-forking sequence** is the implementation requirement. Contradictory approvals on the same previous version are blocked until reconciled. Project QA and product acceptance are separate from the change decision.
5. On chat resume, load the current Task and only the short relevant change summary and any needed final delta. Fetch the whole history only for troubleshooting or end-of-project report. **Never automatically change the source SRS.**
6. Once the project is complete, generate **FOR OWNER DECISION — NOT APPLIED** change comparison, grouped by SRS reference, or by task/feature when still UNMAPPED. Do not create an SRS update PR or sync unless the Owner separately requests it.

## Append-only event format (one Markdown file)

Entries are a short Markdown heading followed by one JSON event in a `pcs-change` fenced block. The event store is machine-validatable, readable in GitHub and searchable by ID, without giant nested JSON blobs. The first event is e.g.:

```pcs-change
{"kind":"PROPOSE","id":"CR-1","task_id":"TASK-5","feature_id":"FEAT-2","item_key":"FEAT-2.password-length","requirement_key":"password-length","srs_ref":"UNMAPPED","mapping":"ACTIVE_CONTEXT","ambiguous_features":false,"based_on":"BASELINE","before":"Tối thiểu 12 ký tự","after":"Tối thiểu 8 ký tự","reason":"Owner thay đổi khi đang làm task","at":"2026-11-01T10:00:00Z"}
```

A later decision is another event with the **same CR ID**: `{"kind":"DECIDE","id":"CR-1","decision":"APPROVED","actor":"owner","ref":"source-of-decision","at":"2026-11-01T10:01:00Z"}`. The decision record alone is not external verification. Do not fabricate refs.

## Agent tools and token limits

- Universal/Desktop (optional Node): `tools/pcs-srs-changes.mjs`
- Chat Solo (optional Python): `tools/pcs_srs_changes.py`
- Read current Task changes (at most **8 different requirement keys** by default): `node tools/pcs-srs-changes.mjs --root=/project --task=TASK-5` (Solo: `python tools/pcs_srs_changes.py --root=/project --task=TASK-5`). Also supports `--feature=FEAT-2`, `--item=FEAT-2.password-length`, `--limit=6`, `--max-items=8`. Check `remaining_items` and request more only when necessary.
- For recording, the Agent creates a short JSON event request and calls `--record=/tmp/change.json --root=/project`; a `PROPOSE` requires the **Agent-inferred** `requirement_key` (e.g. `password-length`), but not an SRS section, Task ID or Feature ID because those are taken from PCS state (Desktop: `--desktop=true`). The Owner never fills in these technical fields. A `DECIDE` event refers to the CR. **Legacy unscoped v1 Feature/Task changes remain readable but must be reconciled before adding scoped records** to the same context; never create a conflicting effective history silently.
- If the Agent works through a GitHub connector rather than CLI, it can append the same format, but must read current blob SHA/revision, validate before updating, use GitHub conditional updates/PR controls and re-read commit. **Do not assume the optional local lock serializes separate GitHub Agents.**
- Tool output is bounded to the selected Task/Feature or a maximum of 8 criteria by default (up to 50 if explicitly requested). Each item shows the **latest approved delta**, not a guaranteed full SRS restatement, plus counts and recent IDs. Large files can be parsed by a local helper without pasting history into the model; read additional context only when needed.
- Initial single-file strategy is deliberately simple. If concurrent writes or file size measurably cause problems, shard by item later behind the same interface. This is **not** automatic today.

**Security / limits:** Enforce repository data classification and access, do not write restricted information in public repos. `verified_external_decision:false` is deliberate; external identity, link, SHA, SRS section mapping and real deployment/tests require independent checks. No new state schema, no changes to the locked Desktop distribution, no automatic migration or SRS sync.
