# Migration analysis — live head `f6b2c4d9a318` → target head `e8c2a5f1b7d4` (pinned RED checkpoint-PFC-B5)

Verified: live `alembic_version` = `f6b2c4d9a318` (read 2026-09-28T03:18Z); pinned tree's single head = `e8c2a5f1b7d4`
(`MIGRATION_STATIC_CHECK::PASS (32 revision(s), single head ['e8c2a5f1b7d4'])`). Seven revisions lie between them, one
linear chain. Applied on the isolated candidate copy of the production database: `MIGRATION_LIVE_CHECK::PASS`, 36 → 43
tables, every existing row kept (2 users, 1 workspace, 2 audit_events). Not applied on live (cutover refused, see report).

| # | Revision | Content | Additive | Destructive | Data rewrite | Downgrade |
|---|---|---|---|---|---|---|
| 1 | `a8d3f1c6e902` f04_system_operation_ai_integrity | audit_events CHECK constraint replaced by a widened one (fifth authority source type); nullable columns + FKs + unique constraints + indexes on `ai_context_manifests`, `ai_derived_artifacts`, `ai_generations`; new tables `ai_operation_authorizations`, `ai_validation_proofs`; immutability triggers; transition trigger function replaced (extended); RLS policies | yes | no (constraint drop is immediately re-created wider; no row can violate a wider set) | no | yes (`downgrade()` present) |
| 2 | `c2e7b9a4f513` f04_question_clusters | new tables `question_clusters`, `question_cluster_memberships` (append-only triggers, RLS) | yes | no | no | yes |
| 3 | `e7c1d4a9b206` f04_accepted_output_binding | trigger functions/triggers only (accepted-output binding rules) | yes | no | no | yes |
| 4 | `a9f3c2e81d57` pfc_f08_committed_events | new table `committed_events` + indexes + immutability triggers + GRANTs to existing roles (`governed_commit_writer`, `api_reader`, `projection_writer`, `audit_reader`, `test_principal` — all present on live) | yes | no | no | yes |
| 5 | `c3b8e5a1f7d2` pfc_f08_projection_aggregate_version | nullable column `last_aggregate_version` on `inquiry_read_model`, `session_read_model` | yes | no | no | yes |
| 6 | `d4f7b2c9e6a1` pfc_b0_fixture_session | column `sessions.fixture` (default false) + immutability trigger; `session_read_model.fixture` | yes | no | no (default fill) | yes |
| 7 | `e8c2a5f1b7d4` pfc_b4_impact_chains | new tables `impact_chains`, `impact_chain_nodes` + triggers + RLS | yes | no | no | yes |

Lock behaviour: DDL on small tables (10 MB database) inside Alembic's transactional DDL; expected duration seconds
(candidate: < 5 s). No migration drops data, rewrites data or touches an object outside the NQUIRY database. No production
decision is required for the migrations themselves.
