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

`domain` still holds no canonical write capability (14 §3.1: "Canonical
write: no") and depends on nothing but `semantic_types`. Every type
here is frozen; a changed canonical record is a new value produced by a
governed CommitUnit, not an in-place edit.
"""
