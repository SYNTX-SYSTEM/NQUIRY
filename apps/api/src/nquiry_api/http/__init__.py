"""HTTP dispatch boundary — extension point only.

`commands.py` (Command dispatch) and `queries.py` (Query dispatch) land
in Phase 4+ (14 §48 file-level implementation map). They must dispatch
through `packages/application` contracts only and must never import an
ORM mutation session or a provider SDK directly (14 §3.1).

Empty in this build phase (Phase 0).
"""
