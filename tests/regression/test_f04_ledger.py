"""F04 WU-04.0 falsifier L-1: the F04 human decisions agree across every ledger home.

MUST BECOME TRUE: 16 §41 REC-018..REC-027, the §6 rows NQ-DEC-044..051, the
machine-readable register (51 decisions, 80 canonical gaps) and 20 §15B
HD-16..HD-23 name the same decisions, and each decision is referenced at its
architecture home file (04 AUTH-DEP-SESS-006, 06 BND-010, 08 §23/§24, 09 §68).

MUST REMAIN IMPOSSIBLE: an F04 semantic choice recorded in one ledger and
missing from another, or a decision without a pointer at its home.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs" / "architecture"

F04_DECISIONS = {
    "HD-16": "NQ-DEC-044",
    "HD-17": "NQ-DEC-045",
    "HD-18": "NQ-DEC-046",
    "HD-19": "NQ-DEC-047",
    "HD-20": "NQ-DEC-048",
    "HD-21": "NQ-DEC-049",
    "HD-22": "NQ-DEC-050",
    "HD-23": "NQ-DEC-051",
}


def _register() -> dict[str, object]:
    text = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    start = text.index("## 37. Machine-Readable Register")
    block = text[start:].split("```yaml", 1)[1].split("\n```", 1)[0]
    return json.loads(block)  # type: ignore[no-any-return]


def test_l1_register_counts() -> None:
    register = _register()
    decisions = register["decisions"]
    assert isinstance(decisions, list)
    assert len(decisions) == 51
    assert len({d["id"] for d in decisions}) == 51
    established = [d for d in decisions if d["status"] == "ESTABLISHED"]
    assert len(established) == 42
    gaps = register["canonical_gaps"]
    assert isinstance(gaps, list)
    assert len(gaps) == 80
    ids = {d["id"]: d for d in decisions}
    for hd, dec in F04_DECISIONS.items():
        assert dec in ids, dec
        assert ids[dec]["source"] == f"F04 {hd}"


def test_l1_records_and_rows_agree() -> None:
    text = (ARCH / "16_DECISION_GAP_REGISTER.md").read_text(encoding="utf-8")
    for n in range(18, 28):
        assert re.search(rf"^### REC-0{n}\b", text, re.MULTILINE), f"REC-0{n}"
    for dec in F04_DECISIONS.values():
        assert re.search(rf"^\| {dec} \|", text, re.MULTILINE), f"§6 row {dec}"


def test_l1_field_engineering_15b_lists_every_f04_decision() -> None:
    text = (ARCH / "20_SYSTEM_FIELD_ENGINEERING.md").read_text(encoding="utf-8")
    section = text.split("## 15B.", 1)[1].split("\n## ", 1)[0]
    for hd, dec in F04_DECISIONS.items():
        assert f"**{hd} ({dec})**" in section, hd


HOMES = {
    "04_AUTHORITY_AND_DECISION_RIGHTS.md": ("# 27. AUTH-DEP-SESS-006", ("HD-16", "HD-17")),
    "06_BOUNDARY_ARCHITECTURE.md": (
        "# 16. BND-010 AI OUTPUT / CANONICAL STATE BOUNDARY",
        ("HD-17",),
    ),
    "08_AI_ARCHITECTURE_AND_CONTRACTS.md": (
        "# 23. AI Operation Contract AIOP-001 QUESTION_ANALYSIS",
        ("HD-16", "HD-18", "HD-19", "HD-20", "HD-22"),
    ),
    "08_AI_ARCHITECTURE_AND_CONTRACTS.md#24": (
        "# 24. AIOP-002 QUESTION_CLUSTERING",
        ("HD-21", "HD-23"),
    ),
    "09_DATA_EVENT_API_CONTRACTS.md": (
        "# 68. Canonicalization Commands for AI Outputs",
        ("HD-17",),
    ),
}


def test_l1_every_decision_is_referenced_at_its_home() -> None:
    for key, (heading, hds) in HOMES.items():
        text = (ARCH / key.split("#", 1)[0]).read_text(encoding="utf-8")
        assert heading in text, heading
        section = text.split(heading, 1)[1].split("\n# ", 1)[0]
        note = section.split("```", 1)[0]
        assert "F04 WU-04.0" in note, f"{key}: no F04 materialization note under {heading}"
        for hd in hds:
            assert hd in note, f"{key}: {hd} missing from the note under {heading}"
