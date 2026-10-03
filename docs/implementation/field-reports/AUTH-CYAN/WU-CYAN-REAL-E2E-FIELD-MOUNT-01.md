# WORK UNIT REPORT
FIELD: NQUIRY_CYAN_SAME_ORIGIN_REVIEW_MOUNT_FIELD
WORK_UNIT: CYAN_REAL_E2E_FIELD_MOUNT_01 — CYAN_OWNED_LOCATION → EXPLICIT_FRONTEND_MOUNT
DATE: 2026-10-03 · BASE: `origin/frontend-symbiotic` @ `32cca350f4c511664c53833b84385aeaf1a57599` (docs over `checkpoint-AUTH-CYAN-IDENTITY-01c`)
AUTHORITY: `HA-AUTH-CYAN.md` → HA-CYAN-REAL-E2E-FIELD-MOUNT-01 (2026-10-03).

## Field reconstruction (before the delta)
| Relation | Finding at the base |
|---|---|
| ORIGIN → FRONTEND MOUNT | implicit: CYAN existed only at the origin root; no mount expression anywhere |
| FRONTEND MOUNT → page routes · internal navigation | Next-owned: `basePath` prefixes routes, `next/link` and the app router (22 call sites: `router.push/replace`, `<Link href>`); no raw root anchors, no `location` writes, no CSS `url()` |
| FRONTEND MOUNT → CYAN static assets | **root-bound**: `components/field/Identity.tsx` `<img src="/brand/…">` (a raw `<img>`, not prefixed by Next) |
| FRONTEND MOUNT → CYAN-owned auth return target | **root-bound**: `app/login/page.tsx` `useProviderContact("/")` |
| ORIGIN → API MOUNT | `NEXT_PUBLIC_API_BASE_URL` (`lib/api/client.ts`), independent of any mount; the OIDC start/link builders and the callback are PURPLE `/api/auth/...` contacts |
| PURPLE → login non-success projection | PURPLE-owned, root-bound `/login?auth=<word>` (`LOGIN_PROJECTION_BASE`); out of scope (BOUNDARY_01), disclosed |

First broken relation: CYAN_OWNED_LOCATION → IMPLICIT_ROOT. Authoritative home for the repair: one CYAN module that
the build config, the asset and the return target derive from.

## Derived implementation (the smallest delta)
| File | Change |
|---|---|
| `apps/web/lib/field/mount.ts` (new) | `normalizeMount` ("" or `/seg(/seg)*`, safe segments, never `/api…`; otherwise throws at build), `FRONTEND_MOUNT` from `NEXT_PUBLIC_FRONTEND_MOUNT`, `mountPath(path)` |
| `apps/web/next.config.ts` | `basePath` = the normalized mount when non-empty; STATE A config is byte-equal to the previous `{ reactStrictMode: true }`; reads no other environment key |
| `apps/web/components/field/Identity.tsx` | brand `src`/`srcSet` via `mountPath` |
| `apps/web/app/login/page.tsx` | `useProviderContact(mountPath("/"))` — the return target is the mount root (re-checks the session and routes onward inside the mount that started the login) |
| `apps/web/playwright.mount.config.ts` (new) | STATE B lane: `next dev -p 3302` with `NEXT_PUBLIC_FRONTEND_MOUNT=/cy-review`, API `http://localhost:8000`, never adopts a foreign server |
| `apps/web/tests/field/mount.test.tsx` (new), `tests/e2e/mount-review.spec.ts` (new) | semantic falsifiers (below) |
| `apps/web/tests/field/{authBoundary,providerContact}.test.tsx` | the page-source law now names the mount root as the return target (successor truth) |
| `apps/web/scripts/mount01-mutation-proof.mjs` (new) | 11 mutations mapping M1–M12 (+M13) |
Not touched: `lib/api/*` (API base, auth contacts, cookies untouched), identity/auth modules, PURPLE, Google configuration, nginx, production, the live root.

## Proof
| Lane | Result |
|---|---|
| Mount semantic falsifiers `tests/field/mount.test.tsx` (normalization; STATE A config `{reactStrictMode:true}`; STATE B config `{reactStrictMode:true, basePath:"/cy-review"}`; API base, start/link contacts and `listProviders` unprefixed under the mount; brand asset prefixed / root; return target = mount root; no raw root asset/navigation in CYAN sources; auth modules never read the mount; config reads only the mount key; identity projection equal under both mounts) | **10 / 10** |
| Full unit suite (gates laws incl. login and workspaces pages) | **622 / 622** (36 files) |
| DEFAULT MOUNT browser proof, sf01 lane `:3301` (auth, cy06-provider, cy07-auth-boundary, cy08-identity, workspaces; desktop + Pixel 7) | **100 / 100** — root behaviour unchanged |
| REVIEW MOUNT browser proof, mount lane `:3302` (`mount-review.spec.ts`, desktop + Pixel 7): `/cy-review/login` served; brand asset `200` at `/cy-review/brand/…`; start href `…/auth/oidc/google/start?next=%2Fcy-review%2F`; zero requests to `/cy-review/api/`; every API request at `http://localhost:8000/…`; local login → `/cy-review/workspaces` with the identity projection; mark links `/cy-review/workspaces`; Logout → `/cy-review/login`; `/cy-review` → `/cy-review/login`; root `/login`, `/workspaces`, `/` → 404 | **8 / 8** |
| Production-mode builds: STATE B (`NEXT_PUBLIC_FRONTEND_MOUNT=/cy-review`, API base `https://nquiry.condyn.eu/api`): `required-server-files` basePath `/cy-review`, 24 `/cy-review/_next/static` refs and 0 root `/_next` refs in `login.html`, 0 `/cy-review/api` refs in server and static output, API base literal `https://nquiry.condyn.eu/api` in the chunks; STATE A: basePath `''`, 24 root `/_next` refs, 0 `/cy-review` refs | both **compiled** |
| `tsc --noEmit`, `eslint .` | clean |
| Mutation proof `scripts/mount01-mutation-proof.mjs` | **11 / 11 killed**, byte-identical restore: M1/M9 mount prefixes the API base · M2 mount ignored · M3/M12 mount forced into the default build · M4 brand asset root-hardcoded · M5 login navigation escapes (raw location write) · M6 Workspaces navigation escapes (raw anchor) · M7 return target escapes the mount · M8 OIDC start moved beneath the mount · M10 mount changes authentication truth · M11 candidate build changes provider configuration · M13 a mount beneath `/api` accepted |
| Not performed, by authority | real production E2E, deployment, nginx change |

## Field reconstruction (after the delta)
```text
ORIGIN https://nquiry.condyn.eu
├─ LIVE FRONTEND MOUNT  /            live CYAN (CY-01 web)            unchanged (no deployment in this unit)
├─ REVIEW FRONTEND MOUNT /cy-review  derivable: STATE B build of the current CYAN (capability only; not deployed)
├─ API MOUNT            /api         production PURPLE                 unchanged; never derived from a frontend mount
│   └─ PURPLE AUTH FIELD: sessions · methods · providers · OIDC start → callback /api/auth/oidc/google/callback   unchanged
├─ SESSION FIELD        nquiry_session host-scoped Path=/             unchanged; shared by both mounts
└─ CYAN PROJECTION      identity · method · provider · boundary      unchanged; mount-independent (proven equal under both)
```
Changed: CYAN_OWNED_LOCATION → FRONTEND_MOUNT and its dependents (brand asset path, auth return target `next`,
build `basePath`). Nothing else.

## Status
CYAN_REAL_E2E_FIELD_MOUNT_01: CLOSED GREEN. Claim ceiling: CURRENT CYAN = FRONTEND_MOUNT_AWARE · DEFAULT ROOT MOUNT =
PRESERVED · CANDIDATE = DERIVABLE AT `/cy-review` · PURPLE API, GOOGLE CALLBACK, AUTHENTICATION FIELD = UNCHANGED ·
REAL PURPLE E2E WITH CURRENT CYAN = NOT YET PROVEN · REAL GOOGLE E2E WITH CURRENT CYAN = NOT YET PROVEN ·
PRODUCTION STAGED REVIEW = NOT YET DEPLOYED.

Next Field boundary (not entered): STAGED_SAME_ORIGIN_E2E_ASSEMBLY.

## Checkpoint
(recorded after commit)
