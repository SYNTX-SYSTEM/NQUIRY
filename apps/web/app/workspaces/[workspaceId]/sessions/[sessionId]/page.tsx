"use client";
/**
 * Session page: the governed inquiry position (F02 WU-02.10).
 *
 * The page shows where the inquiry is (canonical Session state, from the
 * server), what the viewer may do next (server capabilities only), why any
 * other step is unavailable (server reason), who holds Session control and
 * who granted it, and which committed Command established the current state.
 *
 * Navigation reflects state; it never creates state (19 §22). There are no
 * clickable phase tabs. Each step is one semantic Command carrying the
 * version the viewer saw (`expectedVersion`) and one Idempotency-Key per
 * intent. After any Command the page renders the server's re-read, never an
 * assumed result.
 */
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "../../../../../components/f02/AppShell";
import { LoadFailure } from "../../../../../components/f02/LoadFailure";
import { Outcome, type ShownOutcome } from "../../../../../components/f02/Outcome";
import { Unavailable } from "../../../../../components/f02/Unavailable";
import {
  fetchSessionPosition,
  grantSessionControl,
  newIntentKey,
  type QueryResult,
  runSessionCommand,
  type SessionActionName,
  type SessionPosition,
} from "../../../../../lib/api/inquiryClient";

type StepAction = Exclude<SessionActionName, "GRANT_SESSION_CONTROL" | "ADMIT_PARTICIPANT">;

const STEPS: readonly { readonly action: StepAction; readonly label: string; readonly explain: string }[] = [
  { action: "BEGIN_SETUP", label: "Begin setup", explain: "Configure the Session for its method." },
  { action: "BEGIN_CHALLENGE_CAPTURE", label: "Begin challenge capture", explain: "Frame the Challenge for this Session." },
  { action: "PREPARE_BURST", label: "Prepare protected Burst", explain: "Prepare a HUMAN_ONLY question burst." },
  {
    action: "OPEN_QUESTION_GENERATION",
    label: "Open question generation",
    explain: "Starts the protected Burst: humans generate questions, AI is absent.",
  },
];

const PHASE_LABELS: Readonly<Record<string, string>> = {
  DRAFT: "Draft",
  SETUP: "Setup",
  CHALLENGE_CAPTURE: "Challenge capture",
  QUESTION_GENERATION: "Question generation (protected)",
  QUESTION_CAPTURE: "Question capture",
  ANALYSIS: "Analysis",
  REFLECTION: "Reflection",
  QUESTION_SELECTION: "Question selection",
  INVESTIGATION: "Investigation",
  EXPERIMENT: "Experiment",
  ACTION: "Action",
  REVIEW: "Review",
  CLOSED: "Closed",
};

export default function SessionPage() {
  const { workspaceId, sessionId } = useParams<{ workspaceId: string; sessionId: string }>();
  const router = useRouter();
  const [position, setPosition] = useState<QueryResult<SessionPosition> | null>(null);
  const [outcome, setOutcome] = useState<ShownOutcome | null>(null);
  const [busy, setBusy] = useState(false);
  const [intents, setIntents] = useState<Record<string, string>>({});
  const [participant, setParticipant] = useState("");
  const [grantee, setGrantee] = useState("");

  const load = useCallback(() => {
    return fetchSessionPosition(workspaceId, sessionId).then((result) => {
      if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
        router.replace("/login");
        return;
      }
      setPosition(result);
    });
  }, [workspaceId, sessionId, router]);

  useEffect(() => {
    void load();
  }, [load]);

  /** One key per logical intent: reused only for a retry after NO response. */
  function intentFor(name: string): string {
    const existing = intents[name];
    if (existing) return existing;
    const created = newIntentKey();
    setIntents((prev) => ({ ...prev, [name]: created }));
    return created;
  }

  function settle(name: string, networkFailure: boolean) {
    if (!networkFailure) {
      setIntents((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  }

  function run(action: Exclude<SessionActionName, "GRANT_SESSION_CONTROL">, extra: { participantUserId?: string } = {}) {
    if (position?.kind !== "ok") return;
    setBusy(true);
    const key = intentFor(action);
    runSessionCommand(workspaceId, sessionId, action, position.data.session.version, key, extra).then((result) => {
      setBusy(false);
      settle(action, result.kind === "network_failure");
      if (result.kind === "committed") {
        setOutcome({ kind: "committed" });
        setPosition({ kind: "ok", data: result.body.position });
        setParticipant("");
        return;
      }
      setOutcome(
        result.kind === "stale"
          ? { ...result, detail: `The Session is now ${result.currentState ?? "changed"}. Review the current state before acting.` }
          : result,
      );
      void load();
    });
  }

  function grant() {
    setBusy(true);
    const key = intentFor("GRANT");
    grantSessionControl(workspaceId, grantee, { type: "SESSION", id: sessionId }, key).then((result) => {
      setBusy(false);
      settle("GRANT", result.kind === "network_failure");
      setOutcome(result.kind === "committed" ? { kind: "committed" } : result);
      setGrantee("");
      void load();
    });
  }

  if (position === null) {
    return (
      <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: "Session" }]}>
        <p data-testid="session-loading">Loading Session…</p>
      </AppShell>
    );
  }
  if (position.kind !== "ok") {
    return (
      <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: "Session" }]}>
        <LoadFailure failure={position} />
      </AppShell>
    );
  }
  const p = position.data;
  const admit = p.actions.ADMIT_PARTICIPANT;
  const grantCap = p.actions.GRANT_SESSION_CONTROL;

  return (
    <AppShell
      crumbs={[
        { label: "Workspaces", href: "/workspaces" },
        { label: p.workspace.name, href: `/workspaces/${workspaceId}` },
        { label: p.challenge.title ?? "Challenge", href: `/workspaces/${workspaceId}/challenges/${p.challenge.challengeId}` },
        { label: "Session" },
      ]}
    >
      <div className="stack">
        <header>
          <p className="eyebrow">Session · {p.session.method}</p>
          <h1>{p.challenge.title}</h1>
          <p className="lede">
            Inquiry position: <span className="state" data-testid="session-state">{p.session.state}</span>{" "}
            <span className="muted">(version {p.session.version}, canonical)</span>
          </p>
          {!p.workspace.governedFounding ? (
            <p>
              <span className="tag fixture" data-testid="non-proof-fixture">
                NON_PROOF fixture
              </span>{" "}
              <span className="muted">This Session belongs to a development-fixture Workspace. It is not governed proof.</span>
            </p>
          ) : null}
        </header>

        <Outcome outcome={outcome} />

        <div className="grid-2">
          <div className="stack">
            <section className="panel" aria-labelledby="next-title">
              <h2 id="next-title">Next lawful step</h2>
              {STEPS.filter((s) => p.actions[s.action].relevant).length === 0 ? (
                <p className="muted" data-testid="no-next-step">
                  No Session step is available in this phase in the current build.
                </p>
              ) : null}
              <ul className="plain-list">
                {STEPS.filter((s) => p.actions[s.action].relevant).map((s) => {
                  const cap = p.actions[s.action];
                  return (
                    <li key={s.action}>
                      <p style={{ margin: 0 }}>
                        <strong>{s.label}</strong> <span className="muted">— {s.explain}</span>
                      </p>
                      {cap.available ? (
                        <div className="actions-row">
                          <button className="button" type="button" disabled={busy} onClick={() => run(s.action)}>
                            {s.label}
                          </button>
                        </div>
                      ) : (
                        <Unavailable capability={cap} testId={`action-reason-${s.action}`} />
                      )}
                    </li>
                  );
                })}
              </ul>
            </section>

            <section className="panel" aria-labelledby="burst-title">
              <h2 id="burst-title">Protected question burst</h2>
              {p.burst === null ? (
                <p className="muted" data-testid="burst-absent">
                  No burst has been prepared.
                </p>
              ) : (
                <dl className="provenance">
                  <dt>State</dt>
                  <dd>
                    <span className="state" data-testid="burst-state">
                      {p.burst.state}
                    </span>
                  </dd>
                  <dt>Mode</dt>
                  <dd>
                    <span className="tag human" data-testid="burst-mode">
                      {p.burst.mode}
                    </span>{" "}
                    <span className="muted">Only humans author questions. AI is absent while the burst is open.</span>
                  </dd>
                  {p.burst.state === "ACTIVE" ? (
                    <>
                      <dt>Open since</dt>
                      <dd>{p.burst.startedAt ? new Date(p.burst.startedAt).toLocaleString() : "—"}</dd>
                      <dd className="muted" data-testid="capture-not-yet-available">
                        Capturing questions arrives with Field F03. This build shows the lawfully opened burst only.
                      </dd>
                    </>
                  ) : null}
                </dl>
              )}
            </section>

            <section className="panel" aria-labelledby="participants-title">
              <h2 id="participants-title">Participants</h2>
              {p.participants.length === 0 ? (
                <p className="muted" data-testid="participants-empty">
                  No participant has been admitted yet.
                </p>
              ) : (
                <ul className="plain-list" data-testid="participants-list">
                  {p.participants.map((person) => (
                    <li key={person.userId}>
                      <span className="tag human">human</span> <strong>{person.name}</strong>
                    </li>
                  ))}
                </ul>
              )}
              {admit.relevant && admit.available ? (
                <div className="stack">
                  <div className="field">
                    <label htmlFor="admit-participant">Admit participant</label>
                    <select
                      id="admit-participant"
                      value={participant}
                      onChange={(e) => setParticipant(e.target.value)}
                    >
                      <option value="">Choose a member…</option>
                      {p.admitCandidates.map((m) => (
                        <option key={m.userId} value={m.userId}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button
                    className="button secondary"
                    type="button"
                    disabled={busy || participant === ""}
                    onClick={() => run("ADMIT_PARTICIPANT", { participantUserId: participant })}
                  >
                    Admit to Session
                  </button>
                </div>
              ) : admit.relevant ? (
                <Unavailable capability={admit} testId="action-reason-ADMIT_PARTICIPANT" />
              ) : null}
            </section>
          </div>

          <aside className="stack" aria-label="Position and authority">
            <section className="panel" aria-labelledby="phases-title">
              <h2 id="phases-title">Where the inquiry is</h2>
              <ol className="phases" data-testid="session-phases" aria-label="Session phases">
                {p.phases.map((phase) => (
                  <li
                    key={phase.state}
                    data-status={phase.status}
                    aria-current={phase.status === "current" ? "step" : undefined}
                  >
                    <span>{PHASE_LABELS[phase.state] ?? phase.state}</span>
                    <span className="phase-status">
                      {phase.status === "current" ? "current" : phase.status === "done" ? "passed" : ""}
                    </span>
                  </li>
                ))}
              </ol>
            </section>

            <section className="panel" aria-labelledby="authority-title">
              <h2 id="authority-title">Authority</h2>
              <div data-testid="session-authority-provenance" className="provenance">
                {p.sessionControllers.length === 0 ? (
                  <p className="muted">Nobody holds SESSION_CONTROL_RIGHT for this Session yet.</p>
                ) : (
                  <ul className="plain-list">
                    {p.sessionControllers.map((b) => (
                      <li key={b.bindingId}>
                        <span className="tag authority">{b.authorityClass}</span> <strong>{b.holderName}</strong>
                        <div className="muted">
                          granted by {b.grantedByName} · <span className="mono">{b.scope}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
                <p className="muted">
                  You: {p.viewer.role ?? "no role"} ·{" "}
                  {p.viewer.isSessionController ? "Session controller" : "not a Session controller"}
                </p>
              </div>
              {p.establishedBy ? (
                <dl className="provenance" data-testid="session-last-transition">
                  <dt>Current state established by</dt>
                  <dd>
                    <span className="mono">{p.establishedBy.commandType}</span> by {p.establishedBy.actorName ?? "unknown"}
                  </dd>
                  <dt>Authority source</dt>
                  <dd>
                    {p.establishedBy.authoritySourceType ?? "untyped (pre-F02)"}{" "}
                    <span className="mono">{p.establishedBy.authorityScopeRef ?? ""}</span>
                  </dd>
                  <dt>Commit</dt>
                  <dd className="mono">{p.establishedBy.commitId}</dd>
                </dl>
              ) : (
                <p className="muted" data-testid="session-last-transition">
                  No governed commit established this state (fixture-seeded).
                </p>
              )}
            </section>

            {grantCap.available ? (
              <section className="panel" aria-labelledby="gov-title">
                <h2 id="gov-title">Governance</h2>
                <p className="muted">Session control is granted per Session. Nothing is inherited from the Challenge.</p>
                <div className="field">
                  <label htmlFor="grant-session-member">Grant session control to</label>
                  <select id="grant-session-member" value={grantee} onChange={(e) => setGrantee(e.target.value)}>
                    <option value="">Choose a member…</option>
                    {p.grantCandidates.map((m) => (
                      <option key={m.userId} value={m.userId}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="actions-row">
                  <button className="button" type="button" disabled={busy || grantee === ""} onClick={grant}>
                    Grant session control for this Session
                  </button>
                </div>
              </section>
            ) : null}

            <p className="muted">
              <Link href={`/workspaces/${workspaceId}/sessions/${sessionId}/decision`}>Decision surface</Link> (PKG-29
              prototype view)
            </p>
          </aside>
        </div>
      </div>
    </AppShell>
  );
}
