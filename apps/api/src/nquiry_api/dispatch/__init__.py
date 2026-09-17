"""Command/Query dispatch wiring — extension point only.

Routes an HTTP request to the `packages/application` use-case layer.
Must never construct a CommitUnit, touch an ORM session, or call a
provider SDK directly (14 §3.1: controllers forbidden from "ORM
session mutation, provider SDK, direct CommitUnit internals").

Empty in this build phase (Phase 0); materializes with PKG-10 (Command
envelope and attempts) onward.
"""
