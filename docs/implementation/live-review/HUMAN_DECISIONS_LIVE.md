# Human decisions for the live materialization (CYAN-side record; untracked)

## HD-LIVE-1 — HA-20 runtime environment identity of nquiry.condyn.eu (2026-09-28)

**Question (HA-20, PFC queue):** the live deployment configured `NQUIRY_ENVIRONMENT` nowhere; the MockProvider is
dev-runtime only (HD-19) and refused outside DEVELOPMENT / TEST; declaring the live server TEST to obtain mock-derived
output would misstate it.

**Decision (human operator, verbatim):**

> HA-20:
>
> LIVE nquiry.condyn.eu is PRODUCTION.
>
> Production MUST NOT impersonate TEST or DEVELOPMENT
> for the purpose of obtaining MockProvider-derived output.
>
> MockProvider remains unavailable in PRODUCTION.
>
> Therefore:
>
> Real production Sessions may reach ANALYSIS authority,
> but where no legitimate production AI provider is configured,
> the derived Analysis relation remains unavailable / not yet executed
> with the producer's canonical reason.
>
> Do not fabricate ACCEPTED / MOCK / NON_PROOF on real production Sessions.
>
> FIXTURE_NON_PROOF semantics remain preserved where legitimately supported,
> but fixture status does not authorize changing the environment identity.
>
> A future production AI provider requires a separate Field,
> provider authority, configuration, proof and Human review.

**Consequences for the materialization:**
- Cutover delta gains one environment key: `NQUIRY_ENVIRONMENT=PRODUCTION` in `/opt/nquiry/.env` (api service);
  `NQUIRY_AI_PROVIDER` stays unset. Candidate proof with exactly this environment: see the report §10.
- Live `Begin analysis` (TRN-SESS-006) commits under SESSION_CONTROL_RIGHT; the producer's run answers
  `NOT_EXECUTED / AI_PROVIDER_UNAVAILABLE`; the derived field reads "authorized, not yet executed"
  (`PENDING`, reason `AUTHORIZATION_NOT_EXECUTED`), no proof line, no provider — for governed and Fixture Sessions alike.
- The live test plan's Session C end state is that PENDING state, never ACCEPTED / MOCK / NON_PROOF.
- The RED queue row HA-20 is RED's to update (this file is the CYAN-side verbatim copy).
