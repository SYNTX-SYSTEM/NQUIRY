"""ObservationContext and the local OpenTelemetry API sink.

Source: 11_SECURITY_PRIVACY_OBSERVABILITY.md section 36 ("Observability
Constitutional Rule" -- [ARCHITECTURAL CLOSURE] AC-11-013: "OBSERVABILITY
RECONSTRUCTS TECHNICAL BEHAVIOR. OBSERVABILITY DOES NOT DEFINE DOMAIN
TRUTH OR AUTHORITY... Telemetry absence does not prove event absence.
Telemetry presence does not prove domain legitimacy"), section 37
("Observability Correlation Model" -- the exact identity list:
"correlation_id, command_id, attempt_id, commit_id, event_id,
generation_id, recovery_id... A single governed operation should be
traceable across API edge, Command processing, governance evaluation,
boundaries, CommitUnit, outbox, AI Gateway, tool invocation and
recovery without embedding reusable authority into trace context"),
section 38 ("Trace Context Safety" -- the exact "must not carry" list:
"HumanAuthorityBinding as reusable authorization; raw secrets;
authentication tokens; unrestricted Evidence content; full prompts by
default; full provider payloads by default; domain authority decisions
as client-editable attributes... Every receiving component resolves
authoritative state from approved sources rather than trusting trace
annotations"); 14_IMPLEMENTATION_SEQUENCE.md's own PKG-27 OBJECTIVE
("structured ObservationContext and local OpenTelemetry API sink with
correlation_id, command_id, attempt_id, commit_id, event_id,
generation_id, recovery_id, operation, boundary result and failure
class. Minimize content"), the repository-topology row for
`packages/observability/context.py` ("correlation | 11 | semantic_types
| authority tokens | ... | 10").

WHY "MINIMIZE CONTENT" IS STRUCTURAL, NOT A RUNTIME REDACTION STEP
--------------------------------------------------------------------
`ObservationContext` has NO field that could ever hold a secret,
authentication token, raw Evidence content, a full prompt, a full
provider payload, or a HumanAuthorityBinding -- 11 section 38's own
"must not carry" list is satisfied by field-set ABSENCE, the same
non-collapse proof `security.identity.AuthenticatedPrincipal` already
established for IDENTITY != AUTHORITY (no field to smuggle a role
into). `operation`/`boundary_result`/`failure_class` are still
length-capped (see `_MAX_OPERATION_LENGTH`/`_MAX_LABEL_LENGTH` below)
as a SECOND, defense-in-depth guard against using one of these three
permitted string fields as a smuggling vector for exactly the content
11 section 38 forbids (e.g. pasting a full prompt into `operation`).

WHY `boundary_result`/`failure_class` ARE PLAIN, VALUE-MIRRORED STRINGS,
NEVER `boundaries.types.BoundaryResult`/`recovery.failure_classifier.FailureClass`
--------------------------------------------------------------------
14 section 3.1 gives `observability` exactly one allowed dependency:
`semantic_types` -- not `boundaries`, not `recovery`. Same treatment
`audit.models.AuditEvent.result` already gives its own closed-vocabulary
string fields. Unlike that precedent, this module additionally MIRRORS
(never imports) each real enum's own exact value set as a local,
disclosed constant, so an unrecognized value still fails closed (this
package's own NON_COLLAPSE_RULES: "Unknown consequential semantic input
fails closed") rather than being accepted as an arbitrary string.

WHY THIS PACKAGE HOLDS THE `opentelemetry` API IMPORT DIRECTLY, UNLIKE
`persistence`-hosted CONCRETE ADAPTERS (PKG-12/17/23/24/26)
--------------------------------------------------------------------
Those adapters need `sqlalchemy`/`psycopg`, which every package's own
`EXTERNAL_FORBIDDEN` entry (14 section 3.1's own "must not depend on")
already excludes everywhere except `persistence`/`commit`/`ai_gateway`'s
own adapter subfolder. `observability` is instead the ONE package this
codebase designates to hold `opentelemetry` directly (14's own PKG-27
OBJECTIVE literally names "local OpenTelemetry API sink" as this
package's own deliverable) -- `scripts/check_architecture_dependencies.py`'s
own `EXTERNAL_FORBIDDEN["observability"]` entry explicitly permits
`opentelemetry` while still forbidding the web framework/DB driver/
provider SDK groups, the same disclosed, package-specific external-SDK
carve-out `ai_gateway/adapters/providers/` already established for
provider SDKs.

WHY ONLY `opentelemetry-api` IS A RUNTIME DEPENDENCY, NEVER
`opentelemetry-sdk`
--------------------------------------------------------------------
The root `pyproject.toml` (PKG-00's own skeleton) already declares only
`opentelemetry-api` as a runtime dependency -- the OBJECTIVE line's own
wording, "local OpenTelemetry API sink" (API, not SDK), confirms this
is deliberate: production code here calls only `opentelemetry.trace`'s
own API surface (`get_tracer`, `start_as_current_span`,
`set_attribute`), which is safe to call with NO SDK configured at all
(the API package's own default `NoOpTracerProvider` makes every span/
attribute call a real, harmless no-op) -- configuring a real exporter
is a DEPLOYMENT-time concern this package deliberately does not make
for itself. `opentelemetry-sdk` is added as a DEV-ONLY test dependency
(`pyproject.toml`'s own `[project.optional-dependencies].dev`) purely
so `tests/security/test_observability.py` can install an
`InMemorySpanExporter` and prove real span/attribute emission, rather
than merely proving "does not raise" against the default no-op
provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from opentelemetry import trace
from semantic_types.ids import (
    AttemptId,
    CommandId,
    CommitId,
    CorrelationId,
    EventId,
    GenerationId,
    RecoveryId,
)

_MAX_OPERATION_LENGTH = 200
_MAX_LABEL_LENGTH = 100

# 06 §2's own exact 4-value closed vocabulary, mirrored (not imported --
# see this module's own docstring) so an unrecognized value fails
# closed here too.
_KNOWN_BOUNDARY_RESULTS = frozenset({"ALLOW", "DENY", "REQUIRE", "ESCALATE"})

# `recovery.failure_classifier.FailureClass`'s own exact 19-value closed
# vocabulary, mirrored (not imported -- see this module's own
# docstring).
_KNOWN_FAILURE_CLASSES = frozenset(
    {
        "F-VAL",
        "F-AUTH",
        "F-BND",
        "F-CONC",
        "F-PERS",
        "F-PCOM",
        "F-AUD",
        "F-OUT",
        "F-AIGEN",
        "F-AIVAL",
        "F-AITOOL",
        "F-EXT",
        "F-NET",
        "F-PROVDR",
        "F-EVID",
        "F-PROV",
        "F-GOV",
        "F-REC",
        "F-SEC",
    }
)


@dataclass(frozen=True, slots=True)
class ObservationContext:
    """11 section 37's own exact correlation-identity list, plus this
    package's own PKG-27 OBJECTIVE-line additions (`operation`,
    `boundary_result`, `failure_class`). Every field is either a strong,
    non-semantic identity or a short, closed-vocabulary-mirrored label
    -- structurally incapable of carrying secrets, tokens, raw Evidence,
    prompts, or provider payloads (11 section 38's own "must not carry"
    list).
    """

    correlation_id: CorrelationId
    operation: str
    command_id: CommandId | None = None
    attempt_id: AttemptId | None = None
    commit_id: CommitId | None = None
    event_id: EventId | None = None
    generation_id: GenerationId | None = None
    recovery_id: RecoveryId | None = None
    boundary_result: str | None = None
    failure_class: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.correlation_id, CorrelationId):
            raise TypeError(
                f"correlation_id must be a CorrelationId, got {type(self.correlation_id)!r}"
            )
        if not self.operation:
            raise ValueError("ObservationContext.operation must be non-empty")
        if len(self.operation) > _MAX_OPERATION_LENGTH:
            raise ValueError(
                f"ObservationContext.operation must be at most {_MAX_OPERATION_LENGTH} "
                "characters (minimize content, 11 section 38)"
            )
        if self.command_id is not None and not isinstance(self.command_id, CommandId):
            raise TypeError("command_id must be a CommandId or None")
        if self.attempt_id is not None and not isinstance(self.attempt_id, AttemptId):
            raise TypeError("attempt_id must be an AttemptId or None")
        if self.commit_id is not None and not isinstance(self.commit_id, CommitId):
            raise TypeError("commit_id must be a CommitId or None")
        if self.event_id is not None and not isinstance(self.event_id, EventId):
            raise TypeError("event_id must be an EventId or None")
        if self.generation_id is not None and not isinstance(self.generation_id, GenerationId):
            raise TypeError("generation_id must be a GenerationId or None")
        if self.recovery_id is not None and not isinstance(self.recovery_id, RecoveryId):
            raise TypeError("recovery_id must be a RecoveryId or None")
        if self.boundary_result is not None:
            if len(self.boundary_result) > _MAX_LABEL_LENGTH:
                raise ValueError(
                    f"ObservationContext.boundary_result must be at most "
                    f"{_MAX_LABEL_LENGTH} characters"
                )
            if self.boundary_result not in _KNOWN_BOUNDARY_RESULTS:
                raise ValueError(
                    f"ObservationContext.boundary_result {self.boundary_result!r} is not one of "
                    f"06's own closed BoundaryResult vocabulary {sorted(_KNOWN_BOUNDARY_RESULTS)}"
                )
        if self.failure_class is not None:
            if len(self.failure_class) > _MAX_LABEL_LENGTH:
                raise ValueError(
                    f"ObservationContext.failure_class must be at most "
                    f"{_MAX_LABEL_LENGTH} characters"
                )
            if self.failure_class not in _KNOWN_FAILURE_CLASSES:
                raise ValueError(
                    f"ObservationContext.failure_class {self.failure_class!r} is not one of "
                    "10's own closed FailureClass vocabulary"
                )


@runtime_checkable
class ObservationSink(Protocol):
    """Emits an `ObservationContext` somewhere diagnostic. Returns
    `None` -- structurally, nothing here could ever be mistaken for an
    authority proof (this package's own AUTHORITY line: "Never consumed
    as authority proof")."""

    def emit(self, context: ObservationContext) -> None: ...


class LocalOtelObservationSink:
    """The "local OpenTelemetry API sink" 14's own PKG-27 OBJECTIVE
    names. Uses ONLY `opentelemetry.trace`'s own API surface -- see this
    module's own "WHY ONLY opentelemetry-api" docstring section for why
    this is safe (and a real no-op) with no SDK/exporter configured at
    all, and genuinely observable once a real one is (deployment's own
    concern, not this package's).
    """

    def __init__(self, tracer_name: str = "nquiry.observability") -> None:
        self._tracer = trace.get_tracer(tracer_name)

    def emit(self, context: ObservationContext) -> None:
        with self._tracer.start_as_current_span(context.operation) as span:
            span.set_attribute("correlation_id", str(context.correlation_id.value))
            if context.command_id is not None:
                span.set_attribute("command_id", str(context.command_id.value))
            if context.attempt_id is not None:
                span.set_attribute("attempt_id", str(context.attempt_id.value))
            if context.commit_id is not None:
                span.set_attribute("commit_id", str(context.commit_id.value))
            if context.event_id is not None:
                span.set_attribute("event_id", str(context.event_id.value))
            if context.generation_id is not None:
                span.set_attribute("generation_id", str(context.generation_id.value))
            if context.recovery_id is not None:
                span.set_attribute("recovery_id", str(context.recovery_id.value))
            if context.boundary_result is not None:
                span.set_attribute("boundary_result", context.boundary_result)
            if context.failure_class is not None:
                span.set_attribute("failure_class", context.failure_class)


__all__ = ["ObservationContext", "ObservationSink", "LocalOtelObservationSink"]
