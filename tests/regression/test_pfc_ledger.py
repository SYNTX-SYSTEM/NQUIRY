"""PFC ledger: Human Authority decisions of the NQUIRY_PRODUCT_FUNCTION_COMPLETION
Field are recorded in 16 §41, the §6 table, the machine-readable register and
the PFC HUMAN_DECISIONS record, consistently (Architecture 25 §18; 20 §14).

MUST BECOME TRUE (HD-24, HD-25): NQ-DEC-052 / REC-028 and NQ-DEC-053 / REC-029
exist, are ESTABLISHED and name their PFC HD; the register counts are 53
decisions (44 ESTABLISHED), 80 gaps; HA-01 is resolved for Fixture Sessions only;
HA-21 is resolved. HA-22 (ImpactChain authoring authority, recorded after
WU-PFC-B2) is OPEN.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"
PFC = ROOT / "docs" / "implementation" / "field-reports" / "PFC"


def _register() -> dict[str, object]:
    text = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    start = text.index("## 37. Machine-Readable Register")
    block = text[start:].split("```yaml", 1)[1].split("\n```", 1)[0]
    return json.loads(block)  # type: ignore[no-any-return]


def test_register_counts_after_hd_24() -> None:
    decisions = _register()["decisions"]
    assert isinstance(decisions, list)
    assert len(decisions) == 53 and len({d["id"] for d in decisions}) == 53
    assert len([d for d in decisions if d["status"] == "ESTABLISHED"]) == 44
    (dec,) = [d for d in decisions if d["id"] == "NQ-DEC-052"]
    assert dec["source"] == "PFC HD-24" and dec["post_baseline_record"] == "REC-028"


def test_hd_24_is_recorded_everywhere() -> None:
    register = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    assert re.search(r"^### REC-028 / NQ-DEC-052", register, re.MULTILINE)
    assert re.search(r"^\| NQ-DEC-052 \|", register, re.MULTILINE)
    decisions = (PFC / "HUMAN_DECISIONS.md").read_text(encoding="utf-8")
    assert "## HD-24" in decisions and "Option 02 is not selected." in decisions
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-01 |")]
    assert "RESOLVED for Fixture Sessions" in row and "HD-24" in row


def test_hd_25_is_recorded_everywhere() -> None:
    register = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    assert re.search(r"^### REC-029 / NQ-DEC-053", register, re.MULTILINE)
    assert re.search(r"^\| NQ-DEC-053 \|", register, re.MULTILINE)
    (dec,) = [d for d in _register()["decisions"] if d["id"] == "NQ-DEC-053"]  # type: ignore[union-attr]
    assert dec["source"] == "PFC HD-25"
    decisions = (PFC / "HUMAN_DECISIONS.md").read_text(encoding="utf-8")
    assert "## HD-25" in decisions and "HUMAN_PROCEDURAL_CONFIRMATION" in decisions
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-21 |")]
    assert "RESOLVED" in row and "HD-25" in row


def test_the_open_boundaries_hd_24_does_not_close_stay_open() -> None:
    gaps = {g["id"]: g for g in _register()["canonical_gaps"]}  # type: ignore[union-attr]
    assert gaps["NQ-GAP-024"]["status"] == "OPEN"
    assert gaps["NQ-GAP-060"]["status"] == "EXTERNAL_DEPENDENCY"
    assert gaps["NQ-GAP-016"]["status"] == "OPEN"


def test_ha_22_impact_chain_authority_is_queued_open() -> None:
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-22 |")]
    assert row.rstrip().endswith("| OPEN |") and "TRN-SESS-009" in row
