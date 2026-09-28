# WU-PFC-AC1 / AC1.1 — Checkpoint and deployment identity

| Identity | Value |
|---|---|
| AC1 materialization commit | `1a94a586df3400fab08c444d650ab33032894339` (signed); tag `checkpoint-PFC-AC1`, tag object `d430c4efb5cb4e6e502f89d5b3ffa022c596c770` (signed, verified remotely) |
| AC1.1 commit (packaging repair) | `e91961e4a66ab21d9edf45d74bb43b8fbd324737`, tree `af6da710a9c5d81c48f3e84ecadc310e7edabd50` (signed); tag `checkpoint-PFC-AC1.1`, tag object `4bbba5e14744fdff28cbea6297a2674f8a93fe05` (signed, verified remotely) |
| Base | `checkpoint-PFC-B5` → `7d3f74e` (HD-27 producer); records `bb1931a` (HD-28) |
| Tested tree | `evidence/ac1_checksums.txt` (AC1); AC1.1 = AC1 + `pyproject.toml` + `tests/regression/test_packaging_completeness.py` |
| Deployed | 2026-09-28T18:50Z to `nquiry.condyn.eu`, **api only**: assembly `ac11-cy01-20260928T182206Z` (RED AC1.1 + CYAN `field-CY-01` @ `54f8b4f` unchanged), api container `521dac0a4420…`, image `a81b3f47…`; web `2d92fd34…` and postgres unchanged; head `e8c2a5f1b7d4` |
| Rollback | baseline `/opt/nquiry/_baseline-pre-AC1-20260928T181736Z` (compose.yaml.pre, DB dump sha256 `374bc906…`), image tag `nquiry-api:pre-ac1` |

Status: TECHNICALLY_CLOSED, CHECKPOINTED, DEPLOYED. Not REVIEWED_FIELD, not PUBLISHED_FIELD.
