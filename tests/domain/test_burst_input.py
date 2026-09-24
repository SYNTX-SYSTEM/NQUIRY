"""F03 WU-03.5 (HD-12 / NQ-DEC-040): `BURST_INPUT_VALID` is a deterministic
FORM rule.

MUST BECOME TRUE: input is valid iff it contains non-whitespace and its last
non-whitespace character is a question mark in any script (`?`, fullwidth,
Arabic, Greek question mark U+037E, ...). Validation never alters the text.

MUST REMAIN IMPOSSIBLE: a statement / answer / explanation without a final
question mark being valid; empty or whitespace-only input being valid; an
opening mark (`¿`), a `?!` combination or a decorative emoji standing in for a
question mark; a text ending in an invisible character after `?`; a result that
depends on meaning, language or a model; a check that trims or normalizes what
is later stored.

The rule enforces FORM, not MEANING (HD-12: NQ-GAP-023 stays open). The tests
below document that ceiling explicitly.
"""

from __future__ import annotations

import unicodedata

import pytest
from domain.burst_input import (
    BURST_INPUT_MAX_CHARS,
    QUESTION_MARKS,
    BurstInputCheck,
    check_burst_input,
)


@pytest.mark.parametrize(
    "text",
    [
        "Why did it drop?",
        "Why did it drop? ",  # trailing space
        "Why did it drop?\n\t  ",  # trailing whitespace of every kind
        "　Why did it drop？　",  # fullwidth mark, ideographic spaces
        "لماذا؟",  # Arabic
        "πώς;",  # Greek question mark U+037E
        "¿Cómo?",  # Spanish: opening mark plus final ?
        "What ⁉",  # exclamation question mark
        "Really ⁇",  # double question mark
        "?",  # the bare mark is FORM-valid (ceiling, see below)
        "Warum⸮",
        "Line one?\nLine two?",
        "café?",
        "café?",  # combining mark stays as typed
        "\U0001f600 你好？",
    ],
)
def test_valid_form(text: str) -> None:
    check = check_burst_input(text)
    assert check == BurstInputCheck(valid=True, reason_code=None)


@pytest.mark.parametrize(
    "text",
    [
        "It dropped because of onboarding.",  # a statement
        "The answer is yes",
        "Why did it drop? Because of onboarding.",  # question followed by an answer
        "Why did it drop?!",  # ends with '!'
        "Why did it drop⁈",  # QUESTION EXCLAMATION MARK (?!) ends with '!'
        "¿Cómo",  # only the opening mark
        "Why did it drop? ​",  # ends with an invisible ZERO WIDTH SPACE
        "Why did it drop?❓",  # decorative pictograph, not punctuation
        "(Why did it drop?)",  # closing bracket is the last character
        'He asked "why?"',  # closing quote is the last character
        "Why did it drop?.",
    ],
)
def test_invalid_form_is_rejected_as_not_a_question(text: str) -> None:
    check = check_burst_input(text)
    assert check.valid is False
    assert check.reason_code == "INPUT_NOT_A_QUESTION"


@pytest.mark.parametrize("text", ["", " ", "\n\t 　", "   \r\n"])
def test_empty_and_whitespace_only_are_rejected(text: str) -> None:
    check = check_burst_input(text)
    assert check.valid is False
    assert check.reason_code == "INPUT_EMPTY"


def test_length_is_a_technical_safeguard_only() -> None:
    ok = "a" * (BURST_INPUT_MAX_CHARS - 1) + "?"
    assert check_burst_input(ok).valid is True
    too_long = "a" * BURST_INPUT_MAX_CHARS + "?"
    check = check_burst_input(too_long)
    assert check.valid is False and check.reason_code == "INPUT_TOO_LONG"


@pytest.mark.parametrize("text", ["Why\x00?", "Why\ud800?"])
def test_text_the_store_cannot_hold_verbatim_is_rejected_not_altered(text: str) -> None:
    check = check_burst_input(text)
    assert check.valid is False and check.reason_code == "INPUT_NOT_STORABLE"


def test_form_rule_does_not_evaluate_meaning() -> None:
    """DOCUMENTED CEILING (HD-12): a statement that merely ends with '?' passes."""
    assert check_burst_input("The answer is obviously the pricing page?").valid is True
    assert check_burst_input("It is blue?").valid is True


def test_check_never_changes_its_argument_and_is_pure() -> None:
    text = "  Why?  "
    assert check_burst_input(text) == check_burst_input(text)
    assert text == "  Why?  "


def test_question_mark_table_is_explicit_and_matches_unicode() -> None:
    """Every accepted mark is a question-mark punctuation character (Po); the
    table is pinned, so a Unicode upgrade cannot silently change the rule."""
    for cp in QUESTION_MARKS:
        ch = chr(cp)
        assert unicodedata.category(ch) == "Po", hex(cp)
        assert unicodedata.name(ch).endswith("QUESTION MARK"), hex(cp)
    # opening marks, `?!` combinations, pictographs and invisible tags are NOT marks
    for cp in (0xBF, 0x2048, 0x2753, 0x2754, 0x1E95F, 0xE003F):
        assert cp not in QUESTION_MARKS, hex(cp)
    assert 0x3F in QUESTION_MARKS and 0x37E in QUESTION_MARKS and 0xFF1F in QUESTION_MARKS
    assert 0x61F in QUESTION_MARKS
