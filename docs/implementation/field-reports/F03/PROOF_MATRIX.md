# F03 PROOF MATRIX: required proof -> falsifier

All backend tests run against real PostgreSQL (`nquiry_test`) through the real handlers, unless marked HTTP (real routes, real cookies), RS (real-stack browser) or DB (persistence law, bypassing the handler).

| Required proof | Falsifier (test) |
|---|---|
| capture before ACTIVE impossible | `test_capture_burst_question::test_capture_before_the_burst_is_active_is_blocked`; DB `test_f03_membership_law::test_membership_in_prepared_burst_is_refused` |
| capture after completion impossible | `test_complete_burst::test_late_capture_after_the_freeze_is_impossible` (app + DB); HTTP `test_capture_and_completion_flow_over_http`; RS stale-tab `blocked` |
| non-participant capture impossible | `test_non_participants_are_denied[outsider,controller,owner]`; DB `test_membership_for_non_participant_is_refused`, `..._left_participant_...`; BND-014 `test_participation_authority_source` (12); RS owner has no form + API denied |
| foreign Session / Burst capture impossible | `test_participant_of_another_session_cannot_capture_here` |
| cross-Workspace capture impossible | `test_actor_from_another_workspace_is_denied`; DB composite FKs + RLS; RS outsider read + write denied |
| stale capture cannot commit | `test_stale_burst_version_cannot_commit`; HTTP `test_input_and_envelope_outcomes_are_distinct` (409); commit-time STALE via BND-014 (`test_f03_unresolved_capture` FBR-F03-7); real race `test_f03_concurrency` |
| identical retry is idempotent | `test_identical_retry_is_idempotent`; HTTP `test_identical_retry_replays_...` |
| changed-payload key reuse rejected | `test_changed_payload_under_the_same_key_is_rejected`; HTTP same |
| cross-command key reuse rejected | `test_a_key_of_another_command_type_cannot_be_reused_for_capture`, `test_a_capture_key_cannot_be_reused_for_another_command_type`; HTTP cross test |
| original_text cannot mutate | `test_original_text_cannot_be_mutated_once_captured` (DB trigger); static route inventory `test_no_route_can_update_delete_or_rewrite_a_question`; byte-exact round trips (7 Unicode/whitespace cases) + RS `exactText` |
| AI-origin contamination impossible | signature test (no origin/author/mode), non-human actors denied (capture + completion), BND-008 tests (8), HTTP forged `origin`/`authorUserId`/`mode` rejected (5), DB CHECKs + capture-law trigger, static no-AI-import gate |
| manual completion without authority impossible | `test_participants_and_the_owner_cannot_complete`, `test_challenge_scoped_control_does_not_complete`, non-human, other Workspace; RS participant complete `denied` |
| second completion impossible | `test_second_completion_is_blocked_or_replayed` |
| late capture after freeze impossible | see "capture after completion" |
| frozen set contains exactly the committed human questions | `test_denied_and_failed_captures_are_not_in_the_frozen_set`, `test_controller_completes_the_burst_and_freezes_exactly_the_captured_set`, real thread race (acknowledged == frozen) |
| frozen set reconstructs from canonical persistence | `verify_frozen_set` assertions; `test_fingerprint_survives_later_normalization_work`; `test_a_tampered_frozen_set_no_longer_verifies` (control); RS "Verified" on every member's page |
| question and completion provenance are real | capture audit: PARTICIPATION + participation id + `SESSION:<id>`; completion audit: BINDING; `establishedBy` resolves (EC-2 asserted); RS shows CMD_COMPLETE_BURST / BINDING / scope |
| failure before commit creates no partial freeze | `test_failure_before_commit_creates_no_partial_freeze[7 points]` (completion) and capture equivalent; INDETERMINATE tests |
| Timer is presentation only / time creates no effect | `test_time_passing_alone_never_completes_the_burst`; projection has no deadline/remaining field; vitest helper exports no countdown |
| HD-12 questions-only | `test_burst_input` (36), HTTP rejection, RS statement rejected with "Nothing was stored" |
| HD-13 visibility | `test_f03_projection` (own-only, count, frozen for all, payload text absence); legacy view `test_f03_legacy_session_view`; RS Bob/Owner/controller assertions |
| HD-14 self-admission | `test_controller_self_admitted_may_capture_hd14` (BINDING admission audit, PARTICIPATION capture audit); RS controller captures |
| HD-10 / HD-11 | no PAUSE/RESUME Command or route; no scheduler; timer tests |
