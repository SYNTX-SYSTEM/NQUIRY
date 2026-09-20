"""SqlAlchemyWorkspaceContext: the concrete `WorkspaceContextPort`
adapter -- the ONE "trusted server adapter" 14 section 8's own
`[IMPLEMENTATION CHOICE]` names ("transaction-local Workspace context
set only by trusted server adapter").

WHY `set_config(...)` RATHER THAN A LITERAL `SET LOCAL ...` STRING
--------------------------------------------------------------------
PostgreSQL's `SET`/`SET LOCAL` statements do not accept bind
parameters -- a literal string-formatted `SET LOCAL app.workspace_id =
'<value>'` would require manually interpolating a value into SQL text.
`SELECT set_config(name, value, is_local)` is the equivalent
FUNCTION form and DOES accept normal bind parameters, so the
`WorkspaceId`'s own UUID value never touches raw SQL text -- the same
parameterized-query discipline every other write in this codebase
already follows.

WHY CLEARING PASSES AN EMPTY STRING (SEE `security.workspace`'S OWN
MODULE DOCSTRING FOR WHY THE RLS POLICIES TREAT THIS IDENTICALLY TO
"NEVER SET")
--------------------------------------------------------------------
`set_config` cannot set a GUC to SQL NULL. `NULLIF(current_setting(...),
'')::uuid` (used by every RLS policy this package's own migration
creates) collapses both "empty string" and "never set" to the same
fail-closed `NULL` comparison.
"""

from __future__ import annotations

import sqlalchemy as sa
from security.workspace import WORKSPACE_CONTEXT_SETTING
from semantic_types.ids import WorkspaceId


class SqlAlchemyWorkspaceContext:
    """`WorkspaceContextPort` backed by a real SQLAlchemy Core
    connection's own session-local Postgres settings.
    """

    def __init__(self, connection: sa.Connection) -> None:
        self._connection = connection

    def set_workspace_context(self, workspace_id: WorkspaceId) -> None:
        self._connection.execute(
            sa.text("SELECT set_config(:setting, :value, true)"),
            {"setting": WORKSPACE_CONTEXT_SETTING, "value": str(workspace_id.value)},
        )

    def clear_workspace_context(self) -> None:
        self._connection.execute(
            sa.text("SELECT set_config(:setting, '', true)"),
            {"setting": WORKSPACE_CONTEXT_SETTING},
        )


__all__ = ["SqlAlchemyWorkspaceContext"]
