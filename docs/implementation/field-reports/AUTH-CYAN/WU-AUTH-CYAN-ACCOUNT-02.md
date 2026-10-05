# WORK UNIT REPORT
FIELD: NQUIRY_AUTHENTICATION_FIELD × CYAN (complete operational product field)
WORK_UNIT: AUTH/CYAN-ACCOUNT-02 — password rotation in the Access security chamber; membership administration in the Members chamber; the login lockout boundary presented
DATE: 2026-10-05 · BASE: `auth-cyan-reconstruction` @ `c4c6c17` · PURPLE producer: `auth-identity` @ `50ccdb0` (WU-AUTH-19 credential rotation, WU-AUTHZ-01 revoke membership / change role, WU-AUTH-20 login lockout)
AUTHORITY: the human mandate of 2026-10-05 ("complete and close … as a complete operational product field … password lifecycle … workspace membership, roles … revocation").

## Field (before the delta)
| Relation | State |
|---|---|
| a local password's owner rotating it | no contact in the product; the API had none (WU-AUTH-19 adds it) |
| the governance root ending a membership / changing a role | no contact; the API had none (WU-AUTHZ-01 adds them) |
| the login lockout boundary (429 `RATE_LIMITED`) | presented as "Incorrect email or password" |

## Delta (CYAN only)
| File | Change |
|---|---|
| `lib/api/authClient.ts` | `changePassword` / `parsePasswordChange` (`ok {sessionsRevoked}` exact keys; closed denial / rejection vocabularies); producer pin → `50ccdb0` |
| `lib/api/inquiryClient.ts` | `Member.administrable?`, overview capabilities `revokeMembership?` / `changeMemberRole?` (absent on an older producer = not available); `revokeMembershipCommand`, `changeMemberRoleCommand` (F01 envelope) |
| `lib/field/accountSecurity.ts` | `rotatable` = an ACTIVE local method is held |
| `lib/field/accountEffects.ts` | `rotatePassword` Settlement, `CHANGE_PASSWORD_RELATION` |
| `components/field/AccountSecurity.tsx` | `PasswordRotation`: current / new / confirm (password inputs, nothing prefilled, the confirmation the only local check), "your other sessions end · this one continues"; shown only when `rotatable` |
| `app/workspaces/page.tsx` | the rotation effect through the page's effect field; the sessions re-read after it |
| `app/workspaces/[workspaceId]/page.tsx` | `RosterAdministration`: per member the server marks `administrable` (never the viewer, never the root), Change role (only the other role) and Remove, rendered only when the overview's capabilities say so; effects `roster:*` on the shared surface; the roster re-read |
| `app/login/page.tsx` | `RATE_LIMITED` → "Too many attempts. Logging in is paused for a while; try again later." (a denial of the attempt, not a verdict on the credential) |
| `app/globals.css` | password form and roster rows |
| tests | `tests/field/accountSecurity.test.tsx` (+3 P1–P3), `tests/e2e/cy10-roster-admin.spec.ts` (+6 × 2 devices), `tests/e2e/cy09-account-security.spec.ts` (+3 S13–S15), `tests/real-stack/cy09-account-security.real.spec.ts` (+3 real cases), `playwright.sf01.config.ts` (cy10 on the phone project) |

## Proof
| Lane | Result |
|---|---|
| vitest | **675 / 675** |
| tsc · eslint | clean (3 pre-existing warnings) |
| mocked lanes: cy10 **12 / 12**; cy09 + cy08 + cy06 + cy07 + auth + workspaces + sf05 **172 passed** (6 skipped by design) |
| **cross-lineage REAL lane** (`scripts/run_auth_cyan_real_lane.sh`, PURPLE `50ccdb0`, head `e3a5c7d9f1b4`): LOCAL → LINK → LINKED → UNLINK · SESSIONS · PROVIDER_BOOTSTRAP · **PASSWORD ROTATION** (other session ends, this continues, wrong current refused, old password refused, rotated one logs in) · **ROSTER** (root adds, changes the role, ends the membership through the UI; the root is never administrable) · **LOCKOUT** (five wrong → the right password is paused; the page says so) | **12 / 12** (6 × desktop, 6 × Pixel 7) |

## Laws
SERVER CAPABILITY → UI AFFORDANCE (roster controls from the overview capability and the per-member `administrable` verdict, never from a role; the gate `no role- or viewer-flag authority inference` holds) · ROTATION != RECOVERY · the lockout is a boundary of the attempt, not a credential verdict · nothing prefilled, nothing kept · every verdict is the server's.

## Status
TECHNICALLY CLOSED — LOCAL_GREEN + CROSS-LINEAGE REAL PROOF GREEN. Not deployed: the root serves `94759cd`; publication with the PURPLE deployment of `50ccdb0` (both are needed together: the roster contacts and the rotation route live in the api).
