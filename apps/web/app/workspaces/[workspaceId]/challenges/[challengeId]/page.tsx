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
 *
 * SF-01 (21 §12, CF-02, CF-07/08/09): the Challenge regime, the last context
 * before a Session exists.
 * - Position: Workspace → Challenge (current) → Session, which is only a
 *   POSSIBLE relation (server `openSession` available) or UNAVAILABLE (server
 *   reason). No Session coordinate is fabricated before `CreateSession`
 *   commits. After the commit, the newly established Session is entered and
 *   read canonically.
 * - Each existing Session is named by what the server projects (its state and
 *   opening time), not by a client-invented ordinal.
 * - Who holds Session control for this Challenge is authority proof (D2), not
 *   permanent surface width.
 * - A read failure keeps only the confirmed context: the trace falls back to
 *   the access context, and nothing replaces the Challenge (21 §14 NOT_FOUND).
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../../../../components/field/EffectSurface";
import { FieldFrame, FieldLayout, FieldZone } from "../../../../../components/field/FieldFrame";
import { StateName } from "../../../../../components/field/Origin";
import { ProofDepth } from "../../../../../components/field/ProofDepth";
import { ReadBoundary } from "../../../../../components/field/ReadBoundary";
import { Unavailable } from "../../../../../components/f02/Unavailable";
import {
  type ChallengeDetail,
  fetchChallengeDetail,
  grantSessionControl,
  openSession,
  type QueryResult,
} from "../../../../../lib/api/inquiryClient";
import { accessTrace, challengeTrace } from "../../../../../lib/field/position";
import { settleCommand, useEffectField } from "../../../../../lib/field/useEffectField";

const OPEN_SESSION = "open-session";
const GRANT = "grant-challenge-session-control";

const OPENED_AT = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "medium" });

export default function ChallengePage() {
  const { workspaceId, challengeId } = useParams<{ workspaceId: string; challengeId: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<QueryResult<ChallengeDetail> | null>(null);
  const [grantee, setGrantee] = useState("");
  const effect = useEffectField();

  const load = useCallback(
    (): Promise<boolean> =>
      fetchChallengeDetail(workspaceId, challengeId).then((result) => {
        if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
          router.replace("/login");
          return false;
        }
        if (result.kind === "network_failure") {
          // A confirmed projection stays, marked last confirmed by ReconstructionNote.
          setDetail((prev) => (prev?.kind === "ok" ? prev : result));
          return false;
        }
        setDetail(result);
        return result.kind === "ok";
      }),
    [workspaceId, challengeId, router],
  );

  useEffect(() => {
    void load();
  }, [load]);

  function handleOpenSession() {
    void effect.run({
      relation: OPEN_SESSION,
      keyed: true,
      send: async (intentKey) => settleCommand(await openSession(workspaceId, challengeId, intentKey)),
      reconstruct: load,
      onCommitted: (body) => {
        router.push(`/workspaces/${workspaceId}/sessions/${body.sessionId}`);
        return true;
      },
    });
  }

  function handleGrant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void effect.run({
      relation: GRANT,
      keyed: true,
      send: async (intentKey) =>
        settleCommand(await grantSessionControl(workspaceId, grantee, { type: "CHALLENGE", id: challengeId }, intentKey)),
      reconstruct: load,
      onCommitted: () => {
        setGrantee("");
        return false;
      },
    });
  }

  if (detail === null) {
    return (
      <FieldFrame trace={accessTrace("established")} regime="challenge">
        <p data-testid="challenge-loading">Loading Challenge…</p>
      </FieldFrame>
    );
  }
  if (detail.kind !== "ok") {
    return (
      <FieldFrame trace={accessTrace("established")} regime="challenge">
        <ReadBoundary kind={detail.kind} reasonCode={detail.reasonCode} testId="load-failure" />
      </FieldFrame>
    );
  }
  const d = detail.data;

  return (
    <FieldFrame trace={challengeTrace(d)} regime="challenge">
      <header className="field-heading">
        <p className="eyebrow">Challenge</p>
        <h1>{d.challenge.title}</h1>
        {d.challenge.description ? <p className="lede">{d.challenge.description}</p> : null}
      </header>
      <FieldLayout
        primary={
          <>
            <FieldZone zone="centre" labelledBy="sessions-title">
              <ReconstructionNote field={effect.field} />
              <h2 id="sessions-title">Sessions</h2>
              {d.sessions.length === 0 ? (
                <p className="muted" data-testid="sessions-empty">
                  No Session has been opened for this Challenge yet.
                </p>
              ) : (
                <ul className="plain-list" data-testid="sessions-list">
                  {d.sessions.map((s) => (
                    <li key={s.sessionId}>
                      <Link className="card-link" href={`/workspaces/${workspaceId}/sessions/${s.sessionId}`}>
                        Session opened {OPENED_AT.format(new Date(s.createdAt))}
                      </Link>{" "}
                      <StateName state={s.state} />
                    </li>
                  ))}
                </ul>
              )}
            </FieldZone>

            <FieldZone zone="near" labelledBy="open-session-title">
              <h2 id="open-session-title">Open a Session</h2>
              {d.capabilities.openSession.available ? (
                <div className="actions-row">
                  <button className="button" type="button" onClick={handleOpenSession} disabled={effect.blocked}>
                    Open Session
                  </button>
                </div>
              ) : (
                <Unavailable capability={d.capabilities.openSession} testId="session-create-unavailable" />
              )}
              <EffectIntent field={effect.field} relation={OPEN_SESSION} />
              <EffectOutcome field={effect.field} relation={OPEN_SESSION} onReread={() => void effect.rereadNow(load)} />
            </FieldZone>

            {d.capabilities.grantSessionControl.available ? (
              <FieldZone zone="near" labelledBy="grant-title">
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
                    <button className="button" type="submit" disabled={effect.blocked}>
                      Grant session control for this Challenge
                    </button>
                  </div>
                </form>
                <EffectIntent field={effect.field} relation={GRANT} />
                <EffectOutcome field={effect.field} relation={GRANT} onReread={() => void effect.rereadNow(load)} />
              </FieldZone>
            ) : null}
          </>
        }
        secondary={
          <FieldZone zone="depth" label="Authority proof for this Challenge">
            <ProofDepth depth="D2" title="Who holds Session control for this Challenge" testId="challenge-authority-proof">
              {d.sessionControllers.length === 0 ? (
                <p data-testid="challenge-authority-empty">Nobody holds SESSION_CONTROL_RIGHT for this Challenge.</p>
              ) : (
                <ul className="plain-list" data-testid="challenge-authority-list">
                  {d.sessionControllers.map((b) => (
                    <li key={b.bindingId}>
                      <span className="tag authority">{b.authorityClass}</span> <strong>{b.holderName}</strong>
                      <div>
                        granted by {b.grantedByName} · <span className="mono">{b.scope}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </ProofDepth>
          </FieldZone>
        }
      />
    </FieldFrame>
  );
}
