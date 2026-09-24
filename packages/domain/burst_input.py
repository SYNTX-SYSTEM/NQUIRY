"""BURST_INPUT_VALID: the questions-only FORM rule (F03 HD-12).

Source: 06 BND-008 VALIDATION ("For CAPTURE_BURST_QUESTION: input must satisfy
BURST_INPUT_VALID"; the exact validator was GAP-03-003 / NQ-GAP-023). Closed
for the PROTOTYPE by the human operator's decision HD-12 (16 §41 REC-013 /
NQ-DEC-040, 2026-09-24):

    Capture input is BURST_INPUT_VALID when it contains non-whitespace and its
    last non-whitespace character is a question mark in any script. Any other
    input is rejected and nothing is stored. The text itself is stored verbatim;
    validation never alters it.

PROTOTYPE NARROWING. The rule enforces FORM, not MEANING. A statement that ends
with a question mark passes; a real question ending in a closing quote or a
bracket does not. NQ-GAP-023 (a semantic mechanism) stays OPEN, and AI remains
excluded as validator (06 BND-008: "raw Question text sent to evaluator model to
decide quality" is a PROHIBITED PATH). Nothing here calls a model, a network or
a language detector: the result is a pure function of the code points.

TECHNICAL STORAGE SAFEGUARDS (disclosed, Case 2; no product meaning): a maximum
length, and text PostgreSQL cannot store verbatim (NUL, lone surrogates), are
REJECTED, never truncated or altered, because a silent alteration would violate
"original_text stays exact".

QUESTION_MARKS is an explicit, pinned table (Unicode category Po, name ending in
QUESTION MARK, closing/terminal use): opening marks (`¿`, Adlam initial),
`?!` combinations (U+2048) and pictographs (U+2753/2754) are deliberately not
question marks.
"""

from __future__ import annotations

from dataclasses import dataclass

BURST_INPUT_MAX_CHARS = 2000
"""Technical safeguard, not a product rule (F03 readiness O-5)."""

QUESTION_MARKS: frozenset[int] = frozenset(
    {
        0x003F,  # QUESTION MARK
        0x037E,  # GREEK QUESTION MARK
        0x055E,  # ARMENIAN QUESTION MARK
        0x061F,  # ARABIC QUESTION MARK
        0x1367,  # ETHIOPIC QUESTION MARK
        0x1945,  # LIMBU QUESTION MARK
        0x2047,  # DOUBLE QUESTION MARK
        0x2049,  # EXCLAMATION QUESTION MARK
        0x2CFA,  # COPTIC OLD NUBIAN DIRECT QUESTION MARK
        0x2E2E,  # REVERSED QUESTION MARK
        0xA60F,  # VAI QUESTION MARK
        0xA6F7,  # BAMUM QUESTION MARK
        0xFE16,  # PRESENTATION FORM FOR VERTICAL QUESTION MARK
        0xFE56,  # SMALL QUESTION MARK
        0xFF1F,  # FULLWIDTH QUESTION MARK
        0x11143,  # CHAKMA QUESTION MARK
    }
)


@dataclass(frozen=True, slots=True)
class BurstInputCheck:
    valid: bool
    reason_code: str | None = None


def check_burst_input(text: str) -> BurstInputCheck:
    """Pure, deterministic, side-effect free. Never alters `text`."""
    if not isinstance(text, str):
        return BurstInputCheck(False, "INPUT_NOT_STORABLE")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return BurstInputCheck(False, "INPUT_NOT_STORABLE")
    if "\x00" in text:
        return BurstInputCheck(False, "INPUT_NOT_STORABLE")
    stripped_end = text.rstrip()
    if not stripped_end:
        return BurstInputCheck(False, "INPUT_EMPTY")
    if len(text) > BURST_INPUT_MAX_CHARS:
        return BurstInputCheck(False, "INPUT_TOO_LONG")
    if ord(stripped_end[-1]) not in QUESTION_MARKS:
        return BurstInputCheck(False, "INPUT_NOT_A_QUESTION")
    return BurstInputCheck(True, None)


__all__ = ["BURST_INPUT_MAX_CHARS", "QUESTION_MARKS", "BurstInputCheck", "check_burst_input"]
