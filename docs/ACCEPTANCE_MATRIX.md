# PCS Chat Solo — acceptance matrix

Check each capability against the **actual chat platform and a separate private test project repository**. Automated source tests do not replace the real GitHub acceptance checks.

| Case | Expected result | Status (2026-11-01) |
| --- | --- | --- |
| New private project with repository creation permission | Correct repository, initial STATE and Moment persisted and re-read | NOT_RUN |
| Existing repo adoption | Preserve files, branches and unrelated history, resume safely | NOT_RUN |
| New chat/provider after checkpoint | Restores latest verified revision and next action | NOT_RUN |
| Concurrent/stale GitHub revision | No force overwrite, detect conflict, reload/reconcile | NOT_RUN |
| Protected branch checkpoint | PR fallback, not falsely marked APPLIED | NOT_RUN |
| GitHub connector with read-only permissions | Continue safe work, flag PERSISTENCE_BLOCKED | NOT_RUN |
| Evidence and Owner acceptance | Distinguish UI feedback, technical tests and authenticated sensitive approval | NOT_RUN |
| Unit tests and integrity manifest | Automated regression on source commit | PASS in CI when recorded |
| Bounded Moment for 100+ tasks | Summarizes open work instead of dumping all tasks | Covered by unit test |

Use actual run URL, commit SHA, chat platform, repo visibility, expected/actual results and blockers for each manual case before marking PASS. Do not store test secrets or private project data in this public repo.
