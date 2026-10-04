# Cleanup manifest (do not execute until explicitly authorized)

## Live review identities (created 2026-09-28T18:51Z through the host-operator command, HD-28)
| Identity | User id | SecurityEvent (IDENTITY_CREATED) |
|---|---|---|
| `owner@livereview.nquiry.condyn.eu` | `91b04e93-2e75-492f-a3e8-f3400bb0e5bf` | `42089917-e1d2-49c8-94d2-7e21e0f26622` |
| `maya@livereview.nquiry.condyn.eu` | `06b8043d-a83d-4e66-8404-aeb2b6c656fe` | `340c6949-414f-4c29-aff2-04bb8c98fc96` |
| `ravi@livereview.nquiry.condyn.eu` | `99197c0b-b2b8-4efc-87ee-b68bb779453f` | `9a2b085c-afb3-48b3-af56-139282e66601` |
| `elena@livereview.nquiry.condyn.eu` | `2162e130-b7b1-4413-b520-94afc4f586ab` | `90f3fec5-dd08-45f4-bbe8-d863ef12fc28` |

There is no delete, deactivation or reset Command (HD-28 §2; identity lifecycle beyond creation is a separate authority
relation). Removing these identities or revoking their sessions is itself an operation that needs explicit Human
Authority; until then they stay, carrying no authority outside the review Workspace.

## Live review data (created through the product API by the review users)
- Workspace `8311d170-2f30-461f-9085-7a0b9e0e34ac` "NQUIRY LIVE REVIEW 2026-09-28" (founded by the review Owner; governance root = review Owner).
- Memberships: Maya (Facilitator), Ravi (Contributor), Elena (Contributor); Owner (founder).
- Challenge `b9bc6c4c-d419-4091-a223-7f491c6b8a48`.
- Authority bindings: SESSION_CONTROL_RIGHT for Maya at CHALLENGE `b9bc6c4c-d419-4091-a223-7f491c6b8a48` and at SESSION scope for A, B, C, D.
- Sessions: A `95f027cb-c279-5a22-81b6-039f83a6366a` (GOVERNED, QUESTION_CAPTURE), B `d1827699-2cdc-56e2-be3e-e9834d54686c` (FIXTURE_NON_PROOF, QUESTION_CAPTURE),
  C `493dd951-b26d-5605-84d4-de72336325b1` (GOVERNED, ANALYSIS), D `5c257b05-1be6-5a9e-aa9e-9276395bc570` (GOVERNED, ANALYSIS; automation).
- Per Session: one COMPLETED HUMAN_ONLY Burst, participations (Ravi, Elena, Maya), frozen human questions (A 3, B 2, C 3, D 3);
  C and D: one operation authorization each (AIOP-001, NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE).
- Canonical records are append-only by design (commands, audit, outbox, committed events, SecurityEvents). A cleanup is a
  governed-data decision (there is no deletion Command for Sessions, Questions or Workspaces); it needs its own
  authorization and, if chosen, a DB-level procedure recorded as a privileged infrastructure operation (11 §47).

## NQUIRY-owned server resources of this Field
- Assembly `/opt/nquiry/assembly/ac11-cy01-20260928T182206Z/` (the live api build context — keep while deployed).
- Baseline `/opt/nquiry/_baseline-pre-AC1-20260928T181736Z/` (0700: compose.yaml.pre, .env.pre, DB dump
  `nquiry-db-pre-AC1-20260928T181736Z.dump` sha256 374bc906…, digests, preservation snapshots) — keep: rollback material.
- Image tag `nquiry-api:pre-ac1` (the predecessor api image ccb65d79 — rollback anchor).
- Scripts/logs: `/opt/nquiry/ac1-candidate.sh`, `ac1-candidate.log`, `cutover-ac1.sh`, `cutover-ac1.log`.
- The AC1 candidate project `nquiry-ac1-candidate` was already torn down (it held a production data copy): no containers,
  volume, network or image remain. The superseded assembly `ac1-cy01-20260928T181811Z` (never deployed; packaging defect)
  was removed.

## Earlier (CY-01 materialization; unchanged)
- compose project `nquiry-cy01-candidate` (still running on loopback 8401/3401), `/opt/nquiry/candidate/`, helper scripts,
  assembly `cy01-b5-20260928T031904Z` (still the live **web** build context — keep), baseline `_baseline-pre-CY01-…`.
  Teardown commands as before:
  `docker compose -p nquiry-cy01-candidate --env-file /opt/nquiry/candidate/.env -f /opt/nquiry/candidate/compose.yaml down -v --rmi local`
  then `rm -rf /opt/nquiry/candidate`.

## Local (this machine)
- `/tmp/nquiry-live-review/` (0700): `credentials.json`, `state.json`, `NQUIRY_LIVE_TEST_PLAN_WITH_CREDENTIALS.md` (all 0600).
  Delete after the review: `rm -rf /tmp/nquiry-live-review`.
Nothing outside /opt/nquiry, NQUIRY's own compose projects and images, and /tmp/nquiry-live-review was created.
