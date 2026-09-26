# WU-PFC-F09-3 — Telemetry non-interference and governed-Command correlation

**Execution invariant:** EVERY MATERIAL WORK UNIT MUST CLOSE THE FULL SFE PROOF AND RECONSTRUCTION SURFACE (Architecture 25 §23).

## 1. Header

| Item | Value |
|---|---|
| Work Unit / Parent / Child | WU-PFC-F09-3 · NQUIRY_PRODUCT_FUNCTION_COMPLETION · F09 |
| Colour / role / model | RED · observability / application · Claude Opus 5.5 |
| Human authorization | Autonomous SFE execution authorization (2026-09-26). |
| Derivation | 19 §29 internal Work Unit "observability correlation"; TESTS FIRST "telemetry sink failure" (MISSING in the F09 map). |
| Current state / predecessor | `pfc-integration` `b161ff2`; `checkpoint-PFC-F09-2` → `0a05e7c`. |
| Baseline | Live 1849 passed / 2 skipped; no-DB 906 passed. |
| Authoritative home | 11 §36 (AC-11-013), §37 (correlation model), §38 (trace context safety); 12 §20 ("Operational log unavailable -> Audit record remains separately reconstructable"), §25 (minimum causal chain). |
| Authorized delta | The sink never raises. One observation per governed Command at the API edge, carrying identities and the outcome. **Not in scope:** boundary_result / failure_class labels (closed vocabularies; the envelope kind does not map to them without guessing); event, generation or recovery identities per request (they would need DB reads on the request path); exporter configuration (deployment). |
| Must become true | A telemetry outage changes nothing: liveness, governed Commands and delivery passes proceed. Every governed Command is traceable from correlation to command to attempt, plus commit when committed. |
| Must remain true | All outcomes and envelopes; 11 §38 (no authority or content in traces). |
| Must remain impossible | A telemetry failure changing an outcome; a commit identity claimed for a non-committed Command; content, actor or authority in a trace. |
| Falsifiers | `tests/e2e/test_pfc_f09_3_telemetry.py` (7 cases). |

## 2. Execution record
1. **RED.** 7/7 failed for the right reasons: a tracer failure escaped the sink, `/healthz` and the worker pass (×3), and `application.http_f02` had no observation of Commands (×4).
2. **FBR.** `LocalOtelObservationSink.emit` let tracer failures escape, and its callers (`/healthz`, the worker loop) are unguarded. Governed Commands emitted nothing, so the 12 §25 chain had no operational trace at the edge.
3. **Home.** 11 §36–§38; 12 §20, §25.
4. **Repair.**
   - `emit` wraps `_emit` and reports a failure once on stderr. The catch-all is deliberate and documented (AC-11-013: telemetry never changes behaviour).
   - `http_f02._command_outcome(run, ident)` maps the envelope as before (`_command_envelope`) and then emits `ObservationContext(correlation_id, operation="http.command.<kind>", command_id, attempt_id, commit_id only when committed)`.
   - All 8 Command sites (F02/F03 and F04) pass their `ident`.
5. **Propagation.**
   - AFFECTED: the observability sink (all callers: API liveness, worker, Commands) and the `http_f02`/`http_f04` Command sites.
   - NOT AFFECTED: outcomes and envelopes, the persistence of audit/commit (the authoritative chain), CYAN.
6. **Local proof.** ruff, mypy, architecture check (`application → observability` is allowed).
7. **Integration proof.**
   - Real HTTP → PostgreSQL: a Command commits with a broken tracer, and the challenge row exists.
   - The correlation's `commit_id` and `correlation_id` equal the committed `audit_events` row.
   - A denied Command is correlated with no commit.
   - The real worker `main(["--once"])` returns 0 with a broken tracer.
8. **Preservation.** Full regression; the trace-safety falsifier (no title, no actor id).
9. **Regression.** `evidence/f09_3_regression.txt`.
10. **Mutation.** `scripts/pfc_f09_3_mutation_proof.py`: **5/5 KILLED**, sources restored.
11. **Inverse.** An observation `http.command.committed` with `commit_id` C traces to exactly the committed CommitUnit C (audit row), and its `command_id` is the Idempotency-Key. The observation proves nothing by itself (AC-11-013). The audit row is the authority.
12. **Deep sweep.** No authority, content or actor in traces. No decision reads telemetry. The outcome labels are the existing envelope kinds.
13. **Inverse deep sweep.** Every emitted identity comes from the request's `CommandIdentity`, the same object that feeds the CommitUnit.

## 3. Resulting status
**TECHNICALLY_CLOSED, CHECKPOINTED** (`checkpoint-PFC-F09-3`). Not REVIEWED_FIELD, not PUBLISHED_FIELD. F09: IN_PROGRESS.
