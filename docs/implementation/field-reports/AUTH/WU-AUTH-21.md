# WORK UNIT REPORT

FIELD: AUTH — NQIRY IDENTITY & AUTHENTICATION FIELD (PURPLE)
WORK_UNIT: WU-AUTH-21 — production e-mail delivery and the self-service recovery admission (HD-AUTH-10)

| Item | Value |
|---|---|
| ARCHITECTURE_SOURCE | 24 §16.1 (delivery port), §17 (recovery), §24.2 ("recovery links if recovery architecture exists"), §25.2 ("email provider config"), §31.3 (no token outside the message), §36 #11 (resolved by HD-AUTH-10) and #16 (the provider is the operator's choice; the handover is made possible), §45.2 (enumeration) |
| PREDECESSOR | `5674fba` (closure #3) |
| AUTHORITY | **HD-AUTH-10 (2026-10-06):** "A complete production LOCAL_PASSWORD lifecycle requires legitimate self-service recovery through verified e-mail … part of the current Field … reconstruct the complete recovery Field and all dependencies it legitimately entails, including the existing production mail-provider boundary" |
| PROOF_RADIUS | WU-21 falsifiers (9, incl. the real STARTTLS + AUTH transport against an in-test submission service) → WU-11, WU-12, WU-15, WU-18, the sweep: 189 passed |
| HUMAN_AUTHORITY_STATE | HA-AUTH-02 resolved by HD-AUTH-10; the production provider's credentials are an external dependency (below) |

## FIRST_BROKEN_RELATION_BEFORE
RECOVERY → DELIVERY had no production producer: the only mail sink was the
DEVELOPMENT / TEST capture; `VERIFIED_EMAIL_SELF_SERVICE` was refused outside
those environments; a frontend could not know whether recovery leads anywhere.

## DELTA
| File | Change |
|---|---|
| `packages/security/mail.py` | `render_mail` (one message per kind, one absolute link to the frontend's own path with challenge id + token, ASCII 7bit so the link is unbroken), `SmtpSettings` (host, port, sender, `starttls` \| `tls` — plaintext refused, optional credentials together, optional private CA), `smtp_transport` (TLS always, SASL when configured, any refusal → `MailDeliveryFailed`), `SmtpMailSink` (transport injectable), `MailLinks` |
| `packages/application/auth_runtime.py` | `NQUIRY_EMAIL_DELIVERY_MODE=smtp` composes the sink from `NQUIRY_SMTP_HOST / PORT / SECURITY / FROM / USERNAME+PASSWORD / CA_FILE` and requires `NQUIRY_PUBLIC_WEB_BASE_URL`; incomplete → refused at startup; `NQUIRY_EMAIL_VERIFY_PATH`, `NQUIRY_RECOVERY_COMPLETE_PATH` (local destinations); `VERIFIED_EMAIL_SELF_SERVICE` admitted in every declared environment |
| `packages/application/http_recovery.py` | a delivery failure at recovery start rolls the challenge back, is audited (`MAIL_DELIVERY_FAILED`, class only) and keeps the one answer (no enumeration through an outage) |
| `packages/application/http_email.py`, `apps/api/.../http/email.py` | a delivery failure at verification start → `503 unavailable EMAIL_DELIVERY_FAILED` (audited); **`GET /auth/contacts`** → `{kind: ok, recovery: AVAILABLE \| UNAVAILABLE, emailVerification: …}` (public discovery) |
| `packages/security/auth_audit.py` | `MAIL_DELIVERY_FAILED` |
| tests | `tests/e2e/test_auth_wu21_mail_delivery.py` (9); WU-12's production-refusal pin → HD-AUTH-10; sweep: `/auth/contacts` unauthenticated |

## FALSIFIERS
rendering (one link, right path and query, expiry, no address in the text, unknown kind refused) · the sink submits From/To/Auto-Submitted and maps a refusal · settings refuse plaintext, half credentials, empty sender, bad port · the runtime composes the sink only from a complete configuration (each missing fact refused; bad security word refused; a non-local link path refused; a custom path honoured) · self-service recovery admitted in DEVELOPMENT / TEST / STAGING / PRODUCTION, refused undeclared, inert without delivery · failing provider: verification start 503 + no challenge + audited; recovery start the one answer + no challenge + audited · `/auth/contacts` tracks policy × delivery · **the real transport**: STARTTLS negotiated before any MAIL, AUTH PLAIN performed, the message accepted with the link; wrong password refused; untrusted certificate refused (never in the clear); nothing listening → `MailDeliveryFailed`.

## EXTERNAL DEPENDENCY (the remaining boundary of this relation)
The production submission service. Reconstructed read-only on the host: postfix `mail.condyn.eu` listens on 25 / 587 with TLS (Let's Encrypt) and DKIM; `mynetworks` = loopback only and `smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination` — a container on the `nquiry_default` bridge (`172.19.0.1` gateway) is NOT a permitted network, so relay needs **SASL credentials for a sender identity** (e.g. `nquiry@condyn.eu`) created on that mail server by its owner, or an owner's change to the mail server's own configuration (never touched by this Field). Required production values: `NQUIRY_EMAIL_DELIVERY_MODE=smtp`, `NQUIRY_SMTP_HOST=172.19.0.1` (the host's MTA from the compose network) or `mail.condyn.eu`, `NQUIRY_SMTP_PORT=587`, `NQUIRY_SMTP_SECURITY=starttls`, `NQUIRY_SMTP_FROM=<sender>`, `NQUIRY_SMTP_USERNAME/PASSWORD=<the mailbox credentials, never printed>`, `NQUIRY_PUBLIC_WEB_BASE_URL=https://nquiry.condyn.eu`, `NQUIRY_RECOVERY_POLICY=VERIFIED_EMAIL_SELF_SERVICE`. The certificate of `mail.condyn.eu` is public (no CA file); if the host is addressed by IP, the TLS name check needs the hostname — use `mail.condyn.eu` resolved from the container, or the CA file with the right SAN.

## CLAIM_CEILING
PRODUCTION E-MAIL DELIVERY = MATERIALIZED AND PROVEN AGAINST A REAL SUBMISSION PROTOCOL (in-test service); the deployment's provider handover = EXTERNAL (credentials). Recovery and verification become AVAILABLE in production the moment the configuration above is set (one api restart; no migration).
