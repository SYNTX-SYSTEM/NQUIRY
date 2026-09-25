"use client";
/**
 * Challenge Field (22 §23): the primary symbiotic surface.
 *
 * Core = the current Challenge (22 §12.3). Ring 1 = the containment/capability
 * orbit: the New Session relation first (possible → an "Open Session" effect
 * node; unavailable → a blocked relation with the server's reason; 22 §9.11,
 * §23.7) followed by the existing Sessions, each named by what the server
 * projects (state + opening time). Ring 2 = the governance orbit: who holds
 * SESSION_CONTROL_RIGHT at CHALLENGE scope, with grantor and scope (22 §10.8).
 * Planes = instruments (22 §4.8): the effect surface of "Open Session", the
 * grant form (only when the server projects `grantSessionControl`), proof depth.
 *
 * Everything visible resolves to `GET /workspaces/{w}/challenges/{c}`
 * (`inquiry_queries.challenge_detail`); the two effects are
 * `POST …/challenges/{c}/sessions` (CMD_CREATE_SESSION) and
 * `POST …/authority-bindings` (CMD_GRANT_HUMAN_AUTHORITY_BINDING), each through
 * one effect lifecycle: request → server verdict → canonical re-read →
 * reconstructed topology (22 §30, §31). Nothing here computes authority.
 */
import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../../../../components/field/EffectSurface";
import { AuthorityRelation, ChamberHead, Identifiers, ProvenanceSpine } from "../../../../../components/field/chambers";
import { FieldEvent } from "../../../../../components/field/FieldEvent";
import { FieldFrame } from "../../../../../components/field/FieldFrame";
import { StateName } from "../../../../../components/field/Origin";
import { ProofDepth } from "../../../../../components/field/ProofDepth";
import { ReadBoundary } from "../../../../../components/field/ReadBoundary";
import { FieldCore } from "../../../../../components/field/topology/FieldCore";
import { FieldStage, Plane, Planes, Topology } from "../../../../../components/field/topology/FieldStage";
import { Orbit, type OrbitNode, nodeContent } from "../../../../../components/field/topology/Orbit";
import { Unavailable } from "../../../../../components/f02/Unavailable";
import {
  type ChallengeDetail,
  fetchChallengeDetail,
  grantSessionControl,
  openSession,
  type QueryResult,
} from "../../../../../lib/api/inquiryClient";
import type { FieldEventDescription } from "../../../../../lib/field/fieldEvent";
import { accessTrace, challengeTrace } from "../../../../../lib/field/position";
import { affordanceState } from "../../../../../lib/field/topology";
import { settleCommand, useEffectField } from "../../../../../lib/field/useEffectField";

const OPEN_SESSION = "open-session";
const GRANT = "grant-challenge-session-control";

const OPENED_AT = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });

export default function ChallengePage() {
  const { workspaceId, challengeId } = useParams<{ workspaceId: string; challengeId: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<QueryResult<ChallengeDetail> | null>(null);
  const [grantee, setGrantee] = useState("");
  const effect = useEffectField();
  const pendingEvents = useRef<Record<string, FieldEventDescription>>({});

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
        // The new Session is entered: its Field is read canonically there (22 §23.12).
        router.push(`/workspaces/${workspaceId}/sessions/${body.sessionId}`);
        return true;
      },
    });
  }

  function handleGrant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // doc 26 §27, §43.4: the event names the CHALLENGE scope — Challenge control is never described as Session control
    const who = detail?.kind === "ok" ? (detail.data.members.find((m) => m.userId === grantee)?.name ?? "The holder") : "The holder";
    pendingEvents.current[GRANT] = { title: "SESSION CONTROL GRANTED", text: `${who} now holds Session control for this Challenge (CHALLENGE scope; each Session grants its own control).` };
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
      <FieldFrame trace={accessTrace("established")} regime="challenge" exit={null}>
        <FieldStage mode="stack" surface="challenge">
          <FieldCore kind="challenge" state="loading" eyebrow="Challenge" title="Reading the Challenge…" titleAs="p" testId="challenge-loading" />
        </FieldStage>
      </FieldFrame>
    );
  }
  if (detail.kind !== "ok") {
    return (
      <FieldFrame trace={accessTrace("established")} regime="boundary">
        <FieldStage mode="stack" surface="challenge">
          <FieldCore kind="boundary" state="boundary" eyebrow="Boundary" title="This Challenge cannot be projected" titleAs="p" stateText={detail.kind.toUpperCase()} />
          <ReadBoundary kind={detail.kind} reasonCode={detail.reasonCode} testId="load-failure" />
        </FieldStage>
      </FieldFrame>
    );
  }
  const d = detail.data;
  const open = d.capabilities.openSession;
  const newSessionState = affordanceState(open);

  const sessionNodes: OrbitNode[] = [
    {
      key: "new-session",
      state: newSessionState,
      path: newSessionState,
      label: "New Session",
      actionLabel: "Open Session",
      onActivate: open.available ? handleOpenSession : undefined,
      disabled: effect.blocked,
      meta: open.available ? "possible next relation" : "not available now",
      describedBy: open.available ? undefined : "session-create-unavailable",
      testId: "new-session-node",
    },
    ...d.sessions.map(
      (s): OrbitNode => ({
        key: s.sessionId,
        state: "established",
        label: `Session opened ${OPENED_AT.format(new Date(s.createdAt))}`,
        meta: <StateName state={s.state} />,
        href: `/workspaces/${workspaceId}/sessions/${s.sessionId}`,
      }),
    ),
  ];
  const governanceNodes: OrbitNode[] =
    d.sessionControllers.length === 0
      ? [{ key: "no-control", state: "unavailable", path: "governance", label: "Session control", meta: "nobody holds it yet", size: "sm" }]
      : d.sessionControllers.map(
          (b): OrbitNode => ({
            key: b.bindingId,
            state: "governance",
            label: b.holderName,
            meta: `${b.authorityClass} · granted by ${b.grantedByName}`,
            size: "sm",
          }),
        );
  const layoutInput = {
    core: { title: d.challenge.title, stateText: `${d.sessions.length} Sessions`, meta: d.workspace.name },
    rings: [sessionNodes.map((n) => nodeContent(n, "containment")), governanceNodes.map((n) => nodeContent(n, "governance"))],
  };

  return (
    <FieldFrame trace={challengeTrace(d)} regime="challenge">
      <FieldStage layout={layoutInput} surface="challenge">
        <Topology layout={layoutInput}>
          <FieldCore
            kind="challenge"
            state="current"
            eyebrow="Challenge"
            title={d.challenge.title}
            stateText={`${d.sessions.length} ${d.sessions.length === 1 ? "Session" : "Sessions"}`}
            meta={d.workspace.name}
          >
            <ReconstructionNote field={effect.field} />
          </FieldCore>
          <Orbit kind="containment" ring={1} heading="Sessions" nodes={sessionNodes} testId="sessions-list" listAriaLabel="Sessions of this Challenge" />
          <Orbit kind="governance" ring={2} heading="Session control" nodes={governanceNodes} testId="challenge-governance-orbit" listAriaLabel="Session control for this Challenge" />
        </Topology>

        <Planes header={{ eyebrow: "Grown from", title: d.challenge.title, state: `${d.sessions.length} ${d.sessions.length === 1 ? "Session" : "Sessions"}` }}>
          <Plane kind="action" labelledBy="open-session-title">
            <ChamberHead id="open-session-title" semantic="action" title="Open a Session" marker={open.available ? "possible" : "not possible now"} />
            {d.challenge.description ? <p className="lede">{d.challenge.description}</p> : null}
            {d.sessions.length === 0 ? (
              <p className="muted" data-testid="sessions-empty">
                No Session has been opened for this Challenge yet.
              </p>
            ) : null}
            {open.available ? (
              <p className="muted">The Session relation is possible: the “Open Session” node in the field requests it.</p>
            ) : (
              <Unavailable capability={open} testId="session-create-unavailable" />
            )}
            <EffectIntent field={effect.field} relation={OPEN_SESSION} />
            <EffectOutcome field={effect.field} relation={OPEN_SESSION} onReread={() => void effect.rereadNow(load)} />
          </Plane>

          <Plane kind="governance" semantic="authority" labelledBy="grant-title">
            <ChamberHead id="grant-title" semantic="authority" title="Session control for this Challenge" marker="CHALLENGE scope" />
            <p className="chamber-lede">
              Authority is a scoped binding, never a role. Control granted here applies to this Challenge; a Session grants its own control
              separately — nothing is inherited.
            </p>
            <ProofDepth depth="D2" title="Who holds Session control for this Challenge" testId="challenge-authority-proof">
              {d.sessionControllers.length === 0 ? (
                <p data-testid="challenge-authority-empty">Nobody holds SESSION_CONTROL_RIGHT for this Challenge.</p>
              ) : (
                <ul className="authority-chain" data-testid="challenge-authority-list">
                  {d.sessionControllers.map((b) => (
                    <AuthorityRelation
                      key={b.bindingId}
                      bindingKey={b.bindingId}
                      authorityClass={b.authorityClass}
                      holderName={b.holderName}
                      holderKey={b.bindingId}
                      grantedByName={b.grantedByName}
                      scope={b.scope}
                      scopeLabel="this Challenge"
                    />
                  ))}
                </ul>
              )}
            </ProofDepth>
            {d.capabilities.grantSessionControl.available ? (
              <form onSubmit={handleGrant} className="chamber-action">
                <ChamberHead id="grant-form-title" level={3} semantic="action" title="Grant Session control" marker="for this Challenge" />
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
                <EffectIntent field={effect.field} relation={GRANT} />
                <EffectOutcome field={effect.field} relation={GRANT} onReread={() => void effect.rereadNow(load)} />
              </form>
            ) : null}
          </Plane>

          <Plane kind="proof" labelledBy="challenge-proof-title">
            <ChamberHead id="challenge-proof-title" semantic="proof" title="Proof" />
            <ProvenanceSpine
              steps={[
                { kind: "state", label: "Challenge", value: d.challenge.title },
                { kind: "time", label: "Framed", value: OPENED_AT.format(new Date(d.challenge.createdAt)) },
                {
                  kind: "authority",
                  label: "Workspace founding",
                  value: d.workspace.governedFounding ? (
                    "governed (FOUNDING commit recorded)"
                  ) : (
                    <>
                      <span className="tag fixture" data-testid="non-proof-fixture">
                        NON_PROOF fixture
                      </span>{" "}
                      <span className="muted">seeded by a development fixture, not a governed founding.</span>
                    </>
                  ),
                },
              ]}
            />
            <ChamberHead id="challenge-ids-title" level={3} semantic="identifiers" title="Identifiers" />
            <Identifiers items={[{ label: "Challenge", value: d.challenge.challengeId }, { label: "Workspace", value: d.workspace.workspaceId }]} />
          </Plane>
        </Planes>
        <FieldEvent field={effect.field} describe={(relation) => pendingEvents.current[relation] ?? null} />
      </FieldStage>
    </FieldFrame>
  );
}
