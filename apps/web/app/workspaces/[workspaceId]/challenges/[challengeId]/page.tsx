"use client";
/**
 * Challenge page (F02 WU-02.10). The open problem field: its framing, its
 * Sessions, and who may open one.
 *
 * - "Open Session" exists only when the server's `openSession` capability is
 *   available (SESSION_CONTROL_RIGHT at CHALLENGE:<id>, AUTH-DEP-SESS-001).
 *   Otherwise the server's reason is shown and no control is rendered.
 * - The governance panel exists only for the governance root (server
 *   capability `grantSessionControl`). It grants Challenge-scoped Session
 *   control explicitly. No authority is created as a side effect.
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "../../../../../components/f02/AppShell";
import { LoadFailure } from "../../../../../components/f02/LoadFailure";
import { Outcome, type ShownOutcome } from "../../../../../components/f02/Outcome";
import { Unavailable } from "../../../../../components/f02/Unavailable";
import {
  type ChallengeDetail,
  fetchChallengeDetail,
  grantSessionControl,
  newIntentKey,
  openSession,
  type QueryResult,
} from "../../../../../lib/api/inquiryClient";

export default function ChallengePage() {
  const { workspaceId, challengeId } = useParams<{ workspaceId: string; challengeId: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<QueryResult<ChallengeDetail> | null>(null);
  const [outcome, setOutcome] = useState<ShownOutcome | null>(null);
  const [busy, setBusy] = useState(false);
  const [openIntent, setOpenIntent] = useState(newIntentKey);
  const [grantIntent, setGrantIntent] = useState(newIntentKey);
  const [grantee, setGrantee] = useState("");

  const load = useCallback(() => {
    fetchChallengeDetail(workspaceId, challengeId).then((result) => {
      if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
        router.replace("/login");
        return;
      }
      setDetail(result);
    });
  }, [workspaceId, challengeId, router]);

  useEffect(() => {
    load();
  }, [load]);

  function handleOpenSession() {
    setBusy(true);
    openSession(workspaceId, challengeId, openIntent).then((result) => {
      setBusy(false);
      if (result.kind === "committed") {
        setOpenIntent(newIntentKey());
        router.push(`/workspaces/${workspaceId}/sessions/${result.body.sessionId}`);
        return;
      }
      if (result.kind !== "network_failure") setOpenIntent(newIntentKey());
      setOutcome(result);
      load();
    });
  }

  function handleGrant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    grantSessionControl(workspaceId, grantee, { type: "CHALLENGE", id: challengeId }, grantIntent).then((result) => {
      setBusy(false);
      if (result.kind !== "network_failure") setGrantIntent(newIntentKey());
      setOutcome(result.kind === "committed" ? { kind: "committed" } : result);
      load();
    });
  }

  if (detail === null) {
    return (
      <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: "Challenge" }]}>
        <p data-testid="challenge-loading">Loading Challenge…</p>
      </AppShell>
    );
  }
  if (detail.kind !== "ok") {
    return (
      <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: "Challenge" }]}>
        <LoadFailure failure={detail} />
      </AppShell>
    );
  }
  const d = detail.data;

  return (
    <AppShell
      crumbs={[
        { label: "Workspaces", href: "/workspaces" },
        { label: d.workspace.name, href: `/workspaces/${workspaceId}` },
        { label: d.challenge.title },
      ]}
    >
      <div className="stack">
        <header>
          <p className="eyebrow">Challenge</p>
          <h1>{d.challenge.title}</h1>
          {d.challenge.description ? <p className="lede">{d.challenge.description}</p> : null}
        </header>
        <Outcome outcome={outcome} />
        <div className="grid-2">
          <section className="panel" aria-labelledby="sessions-title">
            <h2 id="sessions-title">Sessions</h2>
            {d.sessions.length === 0 ? (
              <p className="muted" data-testid="sessions-empty">
                No Session has been opened for this Challenge yet.
              </p>
            ) : (
              <ul className="plain-list" data-testid="sessions-list">
                {d.sessions.map((s, i) => (
                  <li key={s.sessionId}>
                    <Link className="card-link" href={`/workspaces/${workspaceId}/sessions/${s.sessionId}`}>
                      Session {i + 1}
                    </Link>
                    <span className="state">{s.state}</span>
                  </li>
                ))}
              </ul>
            )}
            {d.capabilities.openSession.available ? (
              <div className="actions-row">
                <button className="button" type="button" onClick={handleOpenSession} disabled={busy}>
                  Open Session
                </button>
              </div>
            ) : (
              <Unavailable capability={d.capabilities.openSession} testId="session-create-unavailable" />
            )}
          </section>

          <aside className="stack" aria-label="Authority for this Challenge">
            <section className="panel" aria-labelledby="controllers-title">
              <h2 id="controllers-title">Session control for this Challenge</h2>
              {d.sessionControllers.length === 0 ? (
                <p className="muted" data-testid="challenge-authority-empty">
                  Nobody holds SESSION_CONTROL_RIGHT for this Challenge.
                </p>
              ) : (
                <ul className="plain-list" data-testid="challenge-authority-list">
                  {d.sessionControllers.map((b) => (
                    <li key={b.bindingId}>
                      <span className="tag authority">{b.authorityClass}</span> <strong>{b.holderName}</strong>
                      <div className="muted">
                        granted by {b.grantedByName} · <span className="mono">{b.scope}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
            {d.capabilities.grantSessionControl.available ? (
              <section className="panel" aria-labelledby="grant-title">
                <h2 id="grant-title">Governance</h2>
                <form onSubmit={handleGrant}>
                  <div className="field">
                    <label htmlFor="grant-member">Grant session control to</label>
                    <select id="grant-member" required value={grantee} onChange={(e) => setGrantee(e.target.value)}>
                      <option value="">Choose a member…</option>
                      {d.members.map((m) => (
                        <option key={m.userId} value={m.userId}>
                          {m.name} ({m.role ?? "no role"})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="actions-row">
                    <button className="button" type="submit" disabled={busy}>
                      Grant session control for this Challenge
                    </button>
                  </div>
                </form>
              </section>
            ) : null}
          </aside>
        </div>
      </div>
    </AppShell>
  );
}
