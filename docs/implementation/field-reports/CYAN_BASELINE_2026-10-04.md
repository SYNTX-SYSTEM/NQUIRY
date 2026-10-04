# CYAN BASELINE — 2026-10-04 (branch `frontend-symbiotic`)

The authoritative, reconstructable state of the CYAN frontend line at this baseline. Everything below is either a
commit/tag that exists on `origin/frontend-symbiotic`, a document in this repository, or an observed runtime fact with
its date. Status words follow Architecture 25 §23: LOCAL_GREEN ≠ FIELD_GREEN ≠ HUMAN_ACCEPTED ≠ REVIEWED_FIELD ≠
PUBLISHED_FIELD ≠ LIVE_PRODUCTION.

## 1. Lineage (tags → commits, newest last)
| Field / Work Unit | Tag → commit | Status |
|---|---|---|
| SF-01…SF-06 symbiotic frontend (docs 21–26) | … `field-SF-06` → `d3d9bd6` | human-reviewed fields; predecessor of CY |
| WU-CY-01 Session position projection (HD-27, RED pin `checkpoint-PFC-B5` `7d3f74e`) | `field-CY-01` → `54f8b4f` | PASS, FIELD_GREEN_WITH_DISCLOSED_CEILINGS; LIVE as the web of `/` (CY-01 web, assembly `cy01-b5-20260928T031904Z`) |
| CYAN-PCPG-01…05 (Architecture 27 v4 `b0a5101`; local lane pin `checkpoint-PFC-PCPG-18` `41b4324`) | `checkpoint-CY-PCPG-01…05` → `6d6c8f8`, `34bcc4d`, `30e0319`, `daeff13`, `2d6163b` | 04 and 05 HUMAN_ACCEPTED (FIELD_GREEN_WITH_DISCLOSED_CEILINGS); not REVIEWED/PUBLISHED; not live |
| AUTH/CYAN-01 typed PURPLE AUTH contract (pin `auth-identity` `aa32c4d`) | `checkpoint-AUTH-CYAN-01` → `5877c13` | LOCAL_GREEN (no presentation) |
| AUTH/CYAN-02 provider contact on the Access Field | `checkpoint-AUTH-CYAN-02` → `b8e7b21` | HUMAN_ACCEPTED 2026-10-03 |
| AUTH/CYAN-03 `?auth=` boundary | `checkpoint-AUTH-CYAN-03` → `bd6534c` | HUMAN_ACCEPTED 2026-10-03 |
| AUTH/CYAN-IDENTITY-01 (+ review delta `…-01b` `841de4e`, field repair `…-01c` `a796526`) | `checkpoint-AUTH-CYAN-IDENTITY-01` → `bf66e45` | CHANGES_REQUESTED then repaired; acceptance moved to the real E2E |
| CYAN_REAL_E2E_FIELD_MOUNT_01 frontend mount | `checkpoint-CYAN-MOUNT-01` → `09f5f0e` | CLOSED GREEN |
| CYAN_REAL_E2E_ASSEMBLY_01 staged `/cy-review/` | (deployment field; records in `AUTH-CYAN/WU-CYAN-REAL-E2E-ASSEMBLY-01.md`) | STAGED, reversible |
| CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01 (pin `auth-identity` `2ec05c0`) | `checkpoint-CYAN-IDENTITY-PRESENTATION-01` → `bfd5300` | TECHNICALLY_PROVEN_AGAINST_PREVIOUS_PURPLE_FIELD; HUMAN_ACCEPTANCE_SUSPENDED (hold `618d7a6`) |

## 2. Runtimes (observed 2026-10-04)
| Runtime | What | Producer |
|---|---|---|
| PRODUCTION `https://nquiry.condyn.eu/` | CY-01 web (`54f8b4f`) | live; untouched by all later CYAN fields |
| PRODUCTION `/api/` | PURPLE assembly `auth-2ec05c0-20261003T223212Z` (identity contact live); PURPLE has since moved to `6395114` PROVIDER_BOOTSTRAP_01 (not consumed) | upstream |
| STAGED `/cy-review/` → 127.0.0.1:3402 | candidate `cyreview-bfd5300-20261003T231217Z` (web only) | this line; rollback `/opt/nquiry/_baseline-pre-CYREVIEW-20261003T213429Z/ROLLBACK.sh` |
| LEGACY candidate stack `nquiry-cy01-candidate` 3401/8401/postgres | 2026-09-28 cutover candidate, still running | lifecycle open (human) |
| LOCAL review `127.0.0.1:13500` (`nquiry-cy01-inspect`) | PCPG-18 producer + CYAN tree of AUTH/CYAN-IDENTITY-01c; proxy fixtures FIXTURE_NON_PROOF (providers, causal sessions/methods, review boundary) | historical for identity; still valid for PCPG review |
| LOCAL lanes | `playwright.sf01.config.ts` :3301 (mocked), `playwright.mount.config.ts` :3302 (review mount), `scripts/run_cy01_real_stack.sh` (RED PCPG-18 producer) | |

## 3. Authoritative documents
Architecture: `docs/architecture/27_…` v4 at `b0a5101` on `pfc-integration` (CYAN), 24 (PURPLE auth) on `auth-identity`,
25 (SFE chain), 26 (PCPG). Ledgers: `field-reports/CY-01/HUMAN_DECISIONS.md` (HD-27), `field-reports/AUTH-CYAN/HA-AUTH-CYAN.md`
(HA-AUTH-CYAN-01…, mount, assembly, identity presentation, HOLD), `live-review/HUMAN_DECISIONS_LIVE.md` (HA-20).
Per field: `WU-*.md` (delta, laws, proof, checkpoint), `HUMAN_REVIEW_GUIDE_*`, `HUMAN_REVIEW_RESULT_*`, `TEST_GUIDE_*`,
`browser-evidence/*/SUMMARY.md`. Evidence images are untracked by convention (`.gitignore`).

## 4. Open boundaries at the baseline
- FIELD_RECONSTRUCTION_HOLD: PURPLE's generic provider-driven identity model; CYAN's "one identity across methods"
  expectation stale; wait for PURPLE's production field, bootstrap behaviour, presentation contract, runtime proof.
- REAL_SAME_ORIGIN_AUTH_E2E on `/cy-review/` — suspended with the hold.
- Lifecycle of the staged mount and of the legacy candidate stack — human.
- CYAN_PRODUCTION_ROOT_CUTOVER — separate field, not authorized.
- RED-side persistence of HD-27 (denied by the execution environment on 2026-09-27) — open.
- Architecture 27 v4 relations not yet materialized in CYAN: attachment rendering of governance deltas onto object
  areas (PCPG-06, map exists since PCPG-03), the deep field inspector (structurally absent), R-13/SEND (not started,
  RED-side), presentation of methods/sessions/link (typed only).

## 5. Standing laws carried forward
PROMPT != AUTHORITY · FRONTEND != AUTHORITY · AUTHENTICATION != AUTHORIZATION · IDENTITY != ROLE != AUTHORITY ·
LINKED_METHOD != CURRENT_METHOD · PROVIDER_EMAIL != CANONICAL_EMAIL · UNKNOWN != OK · TEST_GREEN != FIELD_CLOSED ·
TECHNICAL_PASS != HUMAN_VISUAL_ACCEPTANCE · FIXTURE_NON_PROOF != REAL_RUNTIME_PROOF · consumption never upgrades a
producer · commit/tag/push only on green proof under explicit authority · no passwords in repository files.
