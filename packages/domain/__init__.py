"""domain: Things, Relations, state specs, invariants.

Architectural ownership (14_IMPLEMENTATION_SEQUENCE.md §3.1):
    Responsibility     : Things, Relations, state specs, invariants.
    May depend on      : semantic_types.
    Must not depend on : infrastructure, HTTP, AI SDK.
    Canonical write    : no.

PKG-05 (Build Phase 2) materialized the first domain content here:

- `challenge.Challenge`   — 02 §9 / 09 §25 canonical inquiry frame
- `session.SessionState`  — 03 §13.1's closed 13-state vocabulary
- `session.Session`       — 02 §11 / 09 §27 canonical process object
- `session_transitions`   — 03 §15's TRN-SESS-001..013 as
                            `TransitionSpec` data, plus a topology
                            evaluator that is explicitly *not*
                            authority, boundary or commit

PKG-06 (Build Phase 2) added:

- `question.Question`        — 02 §14 / 09 §31 first-class canonical
                               inquiry object; `original_text` is a
                               permanent birth fact (AC-02-001)
- `question.QuestionOrigin`  — 02 §15's origin axis (AC-02-002),
                               orthogonal to derivation
- `question_lineage.QuestionLineage` — 02 §16 derivation relation
                               (AC-02-003: reframe/follow-up never
                               overwrites the source Question)
- `question_lineage.LineageTransformationType` — 09 §32's REFRAME /
                               FOLLOW_UP

PKG-07 (Build Phase 2) added:

- `burst.BurstState`/`BurstMode`/`QuestionBurst` — 03 §19 4-state
                               machine; `mode` restricted to
                               `HUMAN_ONLY` in this package (08 §12.2/
                               12.3, Mode B/C are successor scope)
- `burst_membership.QuestionBurstMembership` — 02 §17 / 09 §30 frozen
                               raw-capture relation
- `burst_membership.compute_frozen_membership_fingerprint` — 14 §19's
                               `[IMPLEMENTATION CHOICE]` fingerprint
                               algorithm, pure and DB-free
- `burst_transitions`         — 03 §20's TRN-BURST-001..005, reusing
                               `session_transitions`'s generic
                               `BoundaryDependency`/`TransitionProofType`/
                               `ProofObligation`/`ProofRequirement`
                               rather than duplicating them

Note: the BND-008 contamination-guard function (`evaluate_burst_contamination_guard`)
is *not* here — it needs `authority.actor.ActorClass`, which `domain`
may not import (14 §3.1); it lives in `packages/application/burst_contamination.py`
instead, the lowest layer in PKG-07's authorized scope that may depend
on both `domain` and `authority`.

`domain` still holds no canonical write capability (14 §3.1: "Canonical
write: no") and depends on nothing but `semantic_types`. Every type
here is frozen; a changed canonical record is a new value produced by a
governed CommitUnit, not an in-place edit.
"""
