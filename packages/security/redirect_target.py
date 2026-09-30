"""Redirect target validation (24 §11.17, §21.15, §22.8, §32.8; WU-AUTH-06).

REDIRECT TARGET CANDIDATE → VALIDATION → LEGITIMATE LOCAL DESTINATION → REDIRECT

A legitimate local destination is a path of this application: it begins with
exactly one "/", contains only printable ASCII (no whitespace, no control
characters: a redirect header must not be splittable), no backslash (some
browsers read "/\\host" as "//host"), and is short. Everything else, including
an absolute URL, a scheme-relative URL and the provider's own registered
redirect URI, is not a destination of this application.

Two entry points, one rule (`is_legitimate_local_destination`):
`validate_redirect_target` raises for a rejected candidate (the rejected
boundary of 24 §32.8), `resolve_redirect_target` falls back to the safe
default (its other permitted outcome) and is what a login start uses, so a
hostile candidate never blocks a legitimate login and never reaches the
transaction.
"""

from __future__ import annotations

import re

SAFE_DEFAULT_DESTINATION = "/"
MAX_DESTINATION_LENGTH = 1024

# One leading slash; the next character is printable ASCII but neither "/"
# nor "\\" (no scheme-relative form); the rest is printable ASCII without
# space or backslash. Query and fragment are allowed (they stay local).
_LOCAL_DESTINATION = re.compile(r"^/(?:[!-.0-9:-\[\]-~][!-\[\]-~]*)?$")
# A percent-encoded control character (%00-%1F, %7F) is refused as well: it
# is harmless only as long as nothing downstream decodes it before emitting.
_ENCODED_CONTROL = re.compile(r"%(?:[01][0-9A-Fa-f]|7[Ff])")


class RedirectTargetRejected(ValueError):
    """The candidate is not a legitimate local destination. Carries no part
    of the candidate: the rejected value is not echoed anywhere."""

    def __init__(self) -> None:
        super().__init__("redirect target rejected")


def is_legitimate_local_destination(candidate: object) -> bool:
    if not isinstance(candidate, str) or not candidate:
        return False
    if len(candidate) > MAX_DESTINATION_LENGTH:
        return False
    if not candidate.isascii():
        return False
    if _LOCAL_DESTINATION.fullmatch(candidate) is None:
        return False
    return _ENCODED_CONTROL.search(candidate) is None


def validate_redirect_target(candidate: object) -> str:
    if not is_legitimate_local_destination(candidate):
        raise RedirectTargetRejected()
    assert isinstance(candidate, str)
    return candidate


def resolve_redirect_target(candidate: object) -> str:
    """The safe-default form of 24 §32.8: a legitimate candidate is kept, any
    other candidate (including none) becomes `SAFE_DEFAULT_DESTINATION`."""
    if is_legitimate_local_destination(candidate):
        assert isinstance(candidate, str)
        return candidate
    return SAFE_DEFAULT_DESTINATION


__all__ = [
    "MAX_DESTINATION_LENGTH",
    "SAFE_DEFAULT_DESTINATION",
    "RedirectTargetRejected",
    "is_legitimate_local_destination",
    "resolve_redirect_target",
    "validate_redirect_target",
]
