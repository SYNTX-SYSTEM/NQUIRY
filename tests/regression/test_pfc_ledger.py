"""PFC ledger: Human Authority decisions of the NQUIRY_PRODUCT_FUNCTION_COMPLETION
Field are recorded in 16 §41, the §6 table, the machine-readable register and
the PFC HUMAN_DECISIONS record, consistently (Architecture 25 §18; 20 §14).

MUST BECOME TRUE (HD-24..HD-27): NQ-DEC-052 / REC-028, NQ-DEC-053 / REC-029,
NQ-DEC-054 / REC-030 and NQ-DEC-055 / REC-031 exist, are ESTABLISHED and name
their PFC HD, as do NQ-DEC-056 / REC-032 (HD-28); the register counts are 56
decisions (47 ESTABLISHED), 80 gaps;
HA-01 is resolved for Fixture Sessions only; HA-03, HA-21 and HA-22 are
resolved.
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
    assert len(decisions) == 56 and len({d["id"] for d in decisions}) == 56
    assert len([d for d in decisions if d["status"] == "ESTABLISHED"]) == 47
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


def test_hd_26_is_recorded_everywhere() -> None:
    register = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    assert re.search(r"^### REC-030 / NQ-DEC-054", register, re.MULTILINE)
    assert re.search(r"^\| NQ-DEC-054 \|", register, re.MULTILINE)
    (dec,) = [d for d in _register()["decisions"] if d["id"] == "NQ-DEC-054"]  # type: ignore[union-attr]
    assert dec["source"] == "PFC HD-26" and dec["post_baseline_record"] == "REC-030"
    decisions = (PFC / "HUMAN_DECISIONS.md").read_text(encoding="utf-8")
    assert "## HD-26" in decisions and "ImpactChain answer nodes are append-only." in decisions
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-22 |")]
    assert "RESOLVED" in row and "HD-26" in row


def test_ha_23_investigation_completion_is_queued_open() -> None:
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-23 |")]
    assert row.rstrip().endswith("| OPEN |") and "GAP-03-008" in row and "TRN-SESS-010" in row


def test_hd_27_is_recorded_everywhere() -> None:
    register = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    assert re.search(r"^### REC-031 / NQ-DEC-055", register, re.MULTILINE)
    assert re.search(r"^\| NQ-DEC-055 \|", register, re.MULTILINE)
    (dec,) = [d for d in _register()["decisions"] if d["id"] == "NQ-DEC-055"]  # type: ignore[union-attr]
    assert dec["source"] == "PFC HD-27" and dec["post_baseline_record"] == "REC-031"
    decisions = (PFC / "HUMAN_DECISIONS.md").read_text(encoding="utf-8")
    assert "## HD-27" in decisions
    assert "7d3f74e4685b821cc948f45e413c1e0c207259d4" in decisions
    assert "d3d9bd6722bbddabeca56f18d468a8e78bfa294b" in decisions
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-03 |")]
    assert "RESOLVED" in row and "HD-27" in row


def test_hd_28_is_recorded_everywhere() -> None:
    register = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    assert re.search(r"^### REC-032 / NQ-DEC-056", register, re.MULTILINE)
    assert re.search(r"^\| NQ-DEC-056 \|", register, re.MULTILINE)
    (dec,) = [d for d in _register()["decisions"] if d["id"] == "NQ-DEC-056"]  # type: ignore[union-attr]
    assert dec["source"] == "PFC HD-28" and dec["post_baseline_record"] == "REC-032"
    decisions = (PFC / "HUMAN_DECISIONS.md").read_text(encoding="utf-8")
    assert "## HD-28" in decisions and "otti@condyn.eu" in decisions
    queue = (PFC / "HUMAN_AUTHORITY_QUEUE.md").read_text(encoding="utf-8")
    (row,) = [line for line in queue.splitlines() if line.startswith("| HA-24 |")]
    assert "RESOLVED" in row and "HD-28" in row
