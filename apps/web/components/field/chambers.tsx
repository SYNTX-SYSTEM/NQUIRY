/**
 * SF-05 (doc 26 §15–§26, §32–§33) — the shared semantic chamber grammar of the RIGHT_CONTEXT_ORGAN.
 *
 * One contextual organism, many chambers; every chamber carries its SEMANTIC CLASS on the DOM (`data-semantic`) and a
 * recognizable visual role, so that ACTION ≠ AUTHORITY ≠ ROLE ≠ MEMBERSHIP ≠ PARTICIPATION ≠ PROOF ≠ IDENTIFIER ≠
 * BOUNDARY (doc 26 §16). Everything here is projection: the primitives display canonical facts the pages already
 * read and host the request surfaces; none of them decides, infers or stores anything (ROLE != AUTHORITY,
 * MEMBERSHIP != AUTHORITY, HOVER != STATE). Text carries every distinction; colour and geometry only reinforce it.
 */
import type { ReactNode } from "react";

/** Doc 26 §17: the semantic chamber classes of the organ. */
export type SemanticChamber =
  | "context"
  | "action"
  | "authority"
  | "participation"
  | "proof"
  | "question"
  | "frozen"
  | "boundary"
  | "identity"
  | "identifiers"
  | "confirmation"
  | "decision-entry";

/** Doc 26 §26: boundary classes — a boundary is not automatically an error. */
export type BoundaryClass =
  | "NOT_YET_AVAILABLE"
  | "MISSING_AUTHORITY"
  | "MISSING_PARTICIPATION"
  | "MISSING_PREREQUISITE"
  | "IRREVERSIBLE_CONFIRMATION"
  | "SEMANTIC_PROHIBITION"
  | "CURRENTLY_POSSIBLE"
  | "CURRENTLY_NOT_POSSIBLE";

const BOUNDARY_WORDS: Readonly<Record<BoundaryClass, string>> = {
  NOT_YET_AVAILABLE: "not yet available",
  MISSING_AUTHORITY: "missing authority",
  MISSING_PARTICIPATION: "missing participation",
  MISSING_PREREQUISITE: "missing prerequisite",
  IRREVERSIBLE_CONFIRMATION: "irreversible — confirmation required",
  SEMANTIC_PROHIBITION: "not permitted by the system's own law",
  CURRENTLY_POSSIBLE: "currently possible",
  CURRENTLY_NOT_POSSIBLE: "currently not possible",
};

/**
 * The boundary class of a server reason code (projection of the server's own vocabulary; the class never changes
 * the reason, which stays visible verbatim). Unknown codes are CURRENTLY_NOT_POSSIBLE — never an error.
 */
export function boundaryClassOf(reasonCode: string | null | undefined): BoundaryClass {
  const code = (reasonCode ?? "").toUpperCase();
  if (code === "") return "CURRENTLY_NOT_POSSIBLE";
  if (/PARTICIPANT|PARTICIPATION|NOT_ADMITTED/.test(code)) return "MISSING_PARTICIPATION";
  if (/CONTROL|AUTHORITY|GOVERNANCE|BINDING|DENIED|BND_|NOT_A_WORKSPACE_MEMBER|OWNER/.test(code)) return "MISSING_AUTHORITY";
  if (/NOT_IN_STATE|NOT_RELEVANT|STATE_|_NOT_(ACTIVE|PREPARED|OPEN)|ALREADY|COMPLETED|FROZEN|CLOSED|SEQUENCE|PRECONDITION|PREREQ|NO_BURST|BURST_/.test(code)) return "MISSING_PREREQUISITE";
  if (/NOT_YET|LATER|PENDING|UNAVAILABLE_NOW/.test(code)) return "NOT_YET_AVAILABLE";
  if (/FORBIDDEN|PROHIBIT|IMMUTABLE|INVARIANT|AI_/.test(code)) return "SEMANTIC_PROHIBITION";
  return "CURRENTLY_NOT_POSSIBLE";
}

/** A decorative chamber glyph: a small contour per semantic class (aria-hidden; text carries the meaning). */
export function ChamberGlyph({ semantic }: { readonly semantic: SemanticChamber }) {
  return (
    <svg className="chamber-glyph" viewBox="0 0 20 20" aria-hidden="true" focusable="false" data-semantic={semantic}>
      {semantic === "action" ? (
        <>
          <circle cx="6" cy="10" r="3" />
          <path d="M9 10h7m-3-3 3 3-3 3" />
        </>
      ) : semantic === "authority" ? (
        <>
          <circle cx="4" cy="10" r="2" />
          <circle cx="10" cy="10" r="2.6" />
          <circle cx="16" cy="10" r="2" />
          <path d="M6 10h1.5m5 0H14" />
        </>
      ) : semantic === "participation" ? (
        <>
          <circle cx="7" cy="8" r="2.4" />
          <circle cx="13" cy="8" r="2.4" />
          <path d="M3.5 16c.8-3 2.6-4 3.5-4s2.7 1 3.5 4M9.5 16c.8-3 2.6-4 3.5-4s2.7 1 3.5 4" />
        </>
      ) : semantic === "proof" ? (
        <>
          <path d="M6 3v14" />
          <circle cx="6" cy="5" r="1.6" />
          <circle cx="6" cy="10" r="1.6" />
          <circle cx="6" cy="15" r="1.6" />
          <path d="M8 5h8M8 10h6M8 15h8" />
        </>
      ) : semantic === "question" ? (
        <>
          <path d="M4 4h12v9H9l-4 3z" />
          <path d="M8.5 7.2c0-1.2 1-2 2.2-2 1.3 0 2.2.8 2.2 1.9 0 1.3-2.2 1.5-2.2 3" />
          <circle cx="10.7" cy="11.4" r=".6" />
        </>
      ) : semantic === "frozen" ? (
        <>
          <rect x="4" y="9" width="12" height="8" rx="1.5" />
          <path d="M7 9V6.5a3 3 0 0 1 6 0V9" />
          <path d="M10 12v2" />
        </>
      ) : semantic === "boundary" ? (
        <>
          <path d="M3 10h4m6 0h4" strokeDasharray="2 2" />
          <circle cx="10" cy="10" r="2.4" />
        </>
      ) : semantic === "identity" ? (
        <>
          <circle cx="10" cy="10" r="6.5" />
          <circle cx="10" cy="10" r="2" />
        </>
      ) : semantic === "identifiers" ? (
        <>
          <path d="M4 6h12M4 10h8M4 14h10" />
        </>
      ) : semantic === "confirmation" ? (
        <>
          <path d="M10 3l7 12H3z" />
          <path d="M10 8v4" />
          <circle cx="10" cy="13.5" r=".6" />
        </>
      ) : semantic === "decision-entry" ? (
        <>
          <circle cx="10" cy="10" r="6.5" />
          <path d="M10 3.5v13M3.5 10h13" />
        </>
      ) : (
        <>
          <circle cx="10" cy="10" r="5" />
          <circle cx="10" cy="10" r="1.6" />
        </>
      )}
    </svg>
  );
}

/** A chamber heading: glyph · title (the accessible heading) · optional canonical marker text. */
export function ChamberHead({
  id,
  semantic,
  title,
  marker,
  level = 2,
}: {
  readonly id: string;
  readonly semantic: SemanticChamber;
  readonly title: ReactNode;
  /** A canonical marker in words (e.g. "HUMAN_ONLY", "FROZEN", "Challenge scope"); never invented. */
  readonly marker?: ReactNode;
  readonly level?: 2 | 3;
}) {
  const H = level === 2 ? "h2" : "h3";
  return (
    <div className="chamber-head">
      <ChamberGlyph semantic={semantic} />
      <H id={id} className="chamber-title">
        {title}
      </H>
      {marker ? <span className="chamber-marker">{marker}</span> : null}
    </div>
  );
}

/**
 * Doc 26 §20: authority as a relation — AUTHORITY SOURCE → AUTHORITY → HOLDER → SCOPE — never a badge. Every
 * value is a canonical fact from the binding; `held` is the server's own viewer projection when known.
 */
export function AuthorityRelation({
  bindingKey,
  authorityClass,
  holderName,
  holderKey,
  grantedByName,
  scope,
  scopeLabel,
  held,
}: {
  readonly bindingKey: string;
  readonly authorityClass: string;
  readonly holderName: string;
  /** The field entity this holder mirrors (`data-relation-key` ↔ node `data-key`). */
  readonly holderKey?: string;
  readonly grantedByName: string;
  /** The raw canonical scope token, e.g. `CHALLENGE:<id>` or `SESSION:<id>`. */
  readonly scope: string;
  /** The scope in words, e.g. "this Challenge" — CHALLENGE scope ≠ SESSION scope (never inherited). */
  readonly scopeLabel: string;
  readonly held?: boolean;
}) {
  const scopeType = scope.includes(":") ? scope.slice(0, scope.indexOf(":")) : scope;
  return (
    <li className="authority-relation" data-binding={bindingKey} data-scope-type={scopeType} data-held={held === undefined ? undefined : String(held)}>
      <span className="chain-node" data-role="source">
        <span className="chain-role">granted by</span> <span className="chain-value">{grantedByName}</span>
      </span>{" "}
      <span className="chain-link" aria-hidden="true" />
      <span className="chain-node" data-role="authority">
        <span className="chain-role">authority</span>{" "}
        <span className="chain-value tag authority">
          <Token value={authorityClass} bare />
        </span>
      </span>{" "}
      <span className="chain-link" aria-hidden="true" />
      <span className="chain-node" data-role="holder">
        <span className="chain-role">held by</span>{" "}
        <strong className="chain-value" data-relation-key={holderKey}>
          {holderName}
          {held ? <span className="chain-you"> (you)</span> : null}
        </strong>
      </span>{" "}
      <span className="chain-link" aria-hidden="true" />
      <span className="chain-node" data-role="scope">
        <span className="chain-role">scope</span>{" "}
        <span className="chain-value">
          {scopeLabel} <Token value={scope} />
        </span>
      </span>
    </li>
  );
}

export type PersonRelation = "you" | "owner" | "facilitator" | "contributor" | "member" | "participant" | "controller" | "governance-root";

const RELATION_WORDS: Readonly<Record<PersonRelation, string>> = {
  you: "you",
  owner: "Owner role",
  facilitator: "Facilitator role",
  contributor: "Contributor role",
  member: "member",
  participant: "participant",
  controller: "Session controller",
  "governance-root": "governance root",
};

const ROLE_MARKS: Readonly<Record<string, PersonRelation>> = { Owner: "owner", Facilitator: "facilitator", Contributor: "contributor" };

/** The relation mark of a Workspace role: a membership fact projected by lookup (a role is never an authority gate). */
export function roleRelation(role: string | null | undefined): PersonRelation {
  return ROLE_MARKS[role ?? ""] ?? "member";
}

/**
 * Doc 26 §21: one person, several relations — never several people. Roles are membership facts, `controller` is an
 * authority fact, `participant` an admission fact; each is a separate mark so they never collapse into one list.
 */
export function ParticipationRoster({ people, testId, labelledBy }: { readonly people: readonly { readonly userId: string; readonly name: string; readonly relations: readonly PersonRelation[]; readonly relationKey?: string }[]; readonly testId?: string; readonly labelledBy?: string }) {
  return (
    <ul className="roster" data-testid={testId} aria-labelledby={labelledBy}>
      {people.map((person) => (
        <li key={person.userId} className="roster-person" data-user={person.userId}>
          <span className="tag human">human</span>{" "}
          <strong data-relation-key={person.relationKey}>{person.name}</strong>
          <span className="relation-marks">
            {person.relations.map((r) => (
              <span key={r} className="relation-mark" data-relation-kind={r}>
                {RELATION_WORDS[r]}
              </span>
            ))}
          </span>
        </li>
      ))}
    </ul>
  );
}

export type ProvenanceStep = { readonly kind: "state" | "actor" | "authority" | "commit" | "time" | "id"; readonly label: string; readonly value: ReactNode; readonly testId?: string };

/** Doc 26 §22: proof as a provenance spine — CURRENT STATE → ESTABLISHED BY → AUTHORITY SOURCE → COMMIT → TIME. */
export function ProvenanceSpine({ steps, testId }: { readonly steps: readonly ProvenanceStep[]; readonly testId?: string }) {
  return (
    <ol className="spine" data-testid={testId}>
      {steps.map((s, i) => (
        <li key={`${s.kind}-${i}`} className="spine-step" data-kind={s.kind}>
          <span className="spine-point" aria-hidden="true" />
          <span className="spine-label">{s.label}</span>
          <span className="spine-value" data-testid={s.testId}>
            {s.value}
          </span>
        </li>
      ))}
    </ol>
  );
}

/** A technical token that breaks only at its own separators (doc 26 §23): never mid-token, never truncated. */
export function Token({ value, testId, bare = false }: { readonly value: string; readonly testId?: string; readonly bare?: boolean }) {
  const parts = value.split(/(?<=[-_:.])/);
  if (bare) {
    return (
      <>
        {parts.map((p, i) => (
          <span key={i}>
            {p}
            {i < parts.length - 1 ? <wbr /> : null}
          </span>
        ))}
      </>
    );
  }
  return (
    <code className="token" data-testid={testId}>
      {parts.map((p, i) => (
        <span key={i}>
          {p}
          {i < parts.length - 1 ? <wbr /> : null}
        </span>
      ))}
    </code>
  );
}

/** Doc 26 §23: identifiers remain available, contained and copyable; labels above raw ids; never the title. */
export function Identifiers({ items, testId }: { readonly items: readonly { readonly label: string; readonly value: string; readonly testId?: string }[]; readonly testId?: string }) {
  return (
    <dl className="identifiers" data-testid={testId}>
      {items.map((it) => (
        <div key={it.label} className="identifier">
          <dt>{it.label}</dt>
          <dd>
            <Token value={it.value} testId={it.testId} />
            <CopyToken value={it.value} label={it.label} />
          </dd>
        </div>
      ))}
    </dl>
  );
}

function CopyToken({ value, label }: { readonly value: string; readonly label: string }) {
  return (
    <button
      type="button"
      className="copy-token"
      aria-label={`Copy ${label}`}
      title="Copy"
      onClick={() => {
        void navigator.clipboard?.writeText(value);
      }}
    >
      <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
        <rect x="5" y="5" width="8" height="9" rx="1.5" />
        <path d="M3 11V3.5A1.5 1.5 0 0 1 4.5 2H10" />
      </svg>
    </button>
  );
}

/**
 * Doc 26 §26: a boundary with its class in words and structure. The server's reason stays verbatim; the class is a
 * projection of that reason (never a new fact). `role` defaults to none: a boundary is not an alert.
 */
export function BoundaryMark({
  boundary,
  reasonCode,
  testId,
  children,
}: {
  readonly boundary: BoundaryClass;
  readonly reasonCode?: string | null;
  readonly testId?: string;
  readonly children: ReactNode;
}) {
  return (
    <p className="boundary-mark" data-boundary={boundary} data-testid={testId} data-reason-code={reasonCode ?? undefined}>
      <span className="boundary-edge" aria-hidden="true" />
      <span className="boundary-class">{BOUNDARY_WORDS[boundary]}</span>
      <span className="boundary-text">{children}</span>
    </p>
  );
}
