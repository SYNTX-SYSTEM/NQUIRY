# CYAN-RAIL-01 browser evidence (review runtime `nquiry-cy01-inspect`, 127.0.0.1:13500, RED `checkpoint-PFC-PCPG-18`) — 2026-10-04

Real Session `58ed8f33-7074-5593-ad20-2e0382c45941` of Workspace `2c8b7729-…` (facilitator login; no fixture), header
screenshots at three desktop widths with the final CSS (`globals.css` `a8836048…`).

| Width | Route column | Current station (ANALYSIS) | Fits left of the mark | Overlaps the mark | Label box / text advance |
|---|---|---|---|---|---|
| 1024 | ≈ 0–470 | 331–434 (103 px) | yes | no | 79.53 / 79.53 |
| 1280 | ≈ 0–600 | 459–562 (103 px) | yes | no | 79.53 / 79.53 |
| 1440 | ≈ 0–680 | 521–642 (121 px) | yes | no | — |

Before the delta (same runtime, same Session): the `ol` overflowed its column and the chip was drawn over the
wordmark at all three widths; after the flex rule but before the label rule the label box was 79.48 px for a
79.53 px advance and the complete word drew "ANALYS…".

Screenshots (untracked by convention): `screenshots/rail-1024.png`, `rail-1280.png`, `rail-1440.png` — the route
"W… · On… · Where doe… · S. · ANALYSIS" left of the centred mark, "Log out" right.
