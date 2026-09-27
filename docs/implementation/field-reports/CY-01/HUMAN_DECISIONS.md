# CY-01 — HUMAN DECISIONS (CYAN-side record)

The authoritative PFC record is `docs/implementation/field-reports/PFC/HUMAN_DECISIONS.md` and
`HUMAN_AUTHORITY_QUEUE.md` on `pfc-integration`. This file is the CYAN line's own verbatim copy of the decision
that governs it (Architecture 25 §18: the evidence of a Field must let a new agent reconstruct which authority
authorized the Delta). Writing into the RED worktree was refused by the execution environment on 2026-09-27
(shared-resource protection); the RED-side persistence of HD-27 is listed as open in `WU-CY-01.md`.

---

## HD-27 — HA-03 CYAN ↔ RED integration boundary: Option B, pinned checkpoint, separate lines (2026-09-27)

**Question (HA-03 / F04 H-8):** in which order and by which relation does the human-reviewed CYAN line
(`frontend-symbiotic`, tag `field-SF-06`) consume the PFC backend line (`pfc-integration`), given that every CYAN
projection of PFC work (position.analysis, the Challenge frame, freshness/history) needs this integration and that
the standing instruction was "Do not proceed into WU-04.8 unless explicit Human Authority is later provided"?
Options reconstructed from the sources (read-only reconstruction of 2026-09-27): A wait for PUBLISHED_FIELD (SF-01
integration law verbatim); B pin one RED checkpoint, lines stay separate; C merge the pinned checkpoint into CYAN
(WU-SF01.8 form); D track the moving `pfc-integration` head; E RED adopts CYAN and executes WU-04.8 inside RED.

**Decision (human operator, verbatim):**

> HUMAN AUTHORITY DECISION
> HA-03
>
> Choose Option B.
>
> CYAN and RED remain separate Field lines.
>
> CYAN predecessor:
>
> field-SF-06
> → d3d9bd6
> → current human-reviewed symbiotic frontend
>
> RED producer:
>
> checkpoint-PFC-B5
> → 7d3f74e4685b821cc948f45e413c1...
>
> Do NOT consume the moving pfc-integration branch.
>
> Do NOT merge RED into frontend-symbiotic.
>
> Do NOT rebase either line.
>
> Do NOT deploy.
>
> The predecessor for CYAN projection work is the explicit tuple:
>
> CYAN:
> field-SF-06 @ d3d9bd6
>
> RED:
> checkpoint-PFC-B5 @ 7d3f74e4685b821cc948f45e413c1...
>
> Record the full verified RED tag target and commit hash in every CYAN Work Unit that consumes this producer.
>
> Record:
>
> - RED producer checkpoint/tag
> - full RED commit hash
> - RED migration head
> - producer status
> - proof mode
> - exact routes and projection keys consumed
> - CYAN predecessor tag and commit
> - browser/runtime producer identity used for proof
>
> The RED producer ceiling remains explicit:
>
> TECHNICALLY_CLOSED
> CHECKPOINTED
> NOT REVIEWED_FIELD
> NOT PUBLISHED_FIELD
>
> Fixture and mock semantics remain:
>
> FIXTURE_NON_PROOF
> MOCK / NON_PROOF
>
> Consumption by CYAN MUST NOT upgrade the status of RED.
>
> CYAN may project only semantics actually provided by the pinned RED producer.
>
> CYAN must not copy, infer, duplicate or locally stabilize missing RED semantics.
>
> A moving RED branch must never become an implicit producer.
>
> Any change of the pinned RED producer requires a new explicit reconstruction and authorization.
>
> Rollback remains independent:
>
> CYAN → field-SF-06
> RED → checkpoint-PFC-B5
>
> No publication, merge or deployment authority is granted by HA-03.
>
> HA-03 is CLOSED by this decision.
>
> Persist this Human Authority Decision in the authoritative decision record and Human Authority queue.
>
> Then reconstruct the CYAN Field from the new predecessor tuple.
>
> Authorize WU-CY-01 only:
>
> Session Position Projection across the ANALYSIS boundary.
>
> Use the previously reconstructed WU-CY-01 scope exactly.
>
> No redesign.
> No restyle.
> No new page.
> No Reflection.
> No Question Selection.
> No ImpactChain.
> No Investigation.
> No Challenge-frame expansion.
> No backend modification.
>
> Preserve the complete field-SF-06 organism.
>
> Execute the full CYAN SFE proof surface:
>
> FBR
> → baseline
> → recoverable predecessor
> → falsifiers
> → minimum legitimate projection delta
> → mocked browser proof
> → real-stack browser proof
> → responsive proof
> → accessibility proof
> → preservation proof
> → regression proof
> → reconstruction
>
> Expected end status:
>
> READY_FOR_HUMAN_FRONTEND_REVIEW
>
> Do NOT mark FIELD_GREEN.
> Do NOT mark REVIEWED_FIELD.
> Do NOT mark PUBLISHED_FIELD.
>
> After WU-CY-01 is technically closed and reconstructed:
>
> STOP.
>
> Do not start another CYAN Work Unit.
>
> I am the Human Visual Authority for the frontend.

**Verified identities (2026-09-27, `git ls-remote origin` + `git verify-tag`):**

| Line | Tag | Tag object | Target commit | Notes |
|---|---|---|---|---|
| CYAN | `field-SF-06` | `1eb3c14b498a27d6ba277cbc3d4ccd4845074728` | `d3d9bd6722bbddabeca56f18d468a8e78bfa294b` | = `origin/frontend-symbiotic`; human-reviewed symbiotic frontend |
| RED | `checkpoint-PFC-B5` | `fd3d5600132e4dcb9203702d500daccf4c6d0439` (annotated, signed, good signature) | `7d3f74e4685b821cc948f45e413c1e0c207259d4` | tree `bc77cc8bb6414e6104aabdd5bd2fb1874f63f750`; migration head `e8c2a5f1b7d4`; status TECHNICALLY_CLOSED, CHECKPOINTED; not REVIEWED_FIELD, not PUBLISHED_FIELD |

**Ledger:** NQ-DEC-055 · 16 §41 REC-031 — allocated by this record, to be written by the RED line (the register
counts are pinned by RED's `tests/regression/test_pfc_ledger.py`; CYAN does not modify RED).
