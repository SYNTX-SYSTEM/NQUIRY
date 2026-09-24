# F02 Proof-Language Reconciliation Record

Successor record, 2026-09-24, Field F02 (authorized: "Correct proof-language
overclaims where existing browser tests are mocked. Do not delete historical
proof."). Historical reports are **not** edited. This record states how their
browser-proof claims must be read.

## Classes (20_SYSTEM_FIELD_ENGINEERING.md §12)

- **MOCKED BROWSER PROOF**: real Chromium, API responses fulfilled by
  `page.route()`. Proves component/contract behavior only.
- **REAL-STACK BROWSER PROOF**: real browser → web → FastAPI → local auth →
  PostgreSQL (migrated) → governed Commands. No `page.route()`.

## Pre-F02 suites (all MOCKED)

| Spec | `page.route` call sites | Class |
|---|---|---|
| `apps/web/tests/e2e/auth.spec.ts` | 11 | MOCKED |
| `apps/web/tests/e2e/session-view.spec.ts` | 10 | MOCKED |
| `apps/web/tests/e2e/decision.spec.ts` | 9 | MOCKED |
| `apps/web/tests/e2e/workspaces.spec.ts` (F01) | 15 | MOCKED |

## Claims corrected by this record

| Report | Original wording | Correct reading |
|---|---|---|
| `field-reports/F00/WU-00.1.md` L7 | "Playwright 27 passed … Real Chromium, real running containers — login flow, Session-view rendering, Decision recording" | 27 MOCKED browser tests passed. The containers were running, but no test request reached them. F00's runtime proof is its L6 curl/login evidence, not L7 |
| `field-reports/F00/CHATGPT_REVIEW.txt` | "playwright (27 tests) … all PASS" listed among runtime results | MOCKED browser proof |
| `field-reports/F01/CHATGPT_REVIEW.txt` / `FIELD_REVIEW.md` | "10 frontend E2E (real Playwright browser)" | 10 MOCKED browser tests. F01's genuine real-stack evidence is its manual live re-verification ("real founding, real listing, real orientation … zero console errors"), which was not persisted as an automated lane |
| `proof-reports/LOCAL-AUTH-ADAPTER.md` §"Real browser proof: auth.spec.ts" | "real browser" | MOCKED browser proof for the component. Real login was proven separately by curl and manual browser runs |

Unaffected and correctly labelled: `FULLSTACK-RUNTIME-ACCEPTANCE.md` §12
(one-off unmocked Playwright load, explicitly "no `page.route()` mocking")
and §23 (explicitly "network-mocked").

## Going forward

The mocked suites stay as the component-contract lane (`npm run e2e`).
Real-stack proof is `apps/web/tests/real-stack/` (`npm run e2e:real`),
introduced in F02 WU-02.5.
