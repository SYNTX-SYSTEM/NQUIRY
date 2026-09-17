"""No-op worker entrypoint for the Phase 0 skeleton.

Intentionally does nothing but report its own status and exit
successfully. Replaced by real outbox/projection/recovery worker
wiring starting Phase 4 (14 §44). This is not a placeholder pretending
success on a real task — it performs no consequential work and claims
none.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("nquiry_worker: Phase 0 skeleton — no workers implemented yet.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
