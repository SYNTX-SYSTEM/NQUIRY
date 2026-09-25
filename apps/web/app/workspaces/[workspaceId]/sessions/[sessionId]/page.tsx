"use client";
/**
 * Session Field (22 §24–§26): a reconstructing lifecycle Field, not a process page.
 *
 * Core = the current Session (22 §12.4). Its identity SHIFTS with the canonical
 * lifecycle: during `QUESTION_GENERATION` with an ACTIVE HUMAN_ONLY Burst the
 * core is the Human Question Field (22 §12.5, cyan, `data-core-state="human"`);
 * after `CMD_COMPLETE_BURST` it is the frozen human question set (22 §12.6,
 * blue, `frozen`); otherwise the Session in its state. Ring 1 = the lifecycle
 * orbit: every canonical state the server projects (`phases`, 13 states), with
 * label density following gravity (passed, current and next labelled; later
 * states as dots with assistive labels; 22 §16.2). Ring 2 = the relation orbit:
 * participants (human nodes) and Session controllers (governance nodes with
 * grantor and scope). Planes = instruments in semantic order (22 §32.6): the
 * active phase (lawful next transitions, the protected Burst surface or the
 * frozen artifact), governance (control, participation, grant), proof.
 *
 * Human Question Law (22 §4.5) is the server's: capture exists only while the
 * server projects `CAPTURE_QUESTION` in QUESTION_GENERATION / ACTIVE HUMAN_ONLY;
 * the frozen set exists only when the server projects `questionSet.frozen`.
 * Every command carries the version the viewer saw and one Idempotency-Key per
 * intent, runs through ONE effect lifecycle and is followed by a canonical
 * re-read of `GET …/sessions/{s}/position` before the topology changes (22 §30).
 * Nothing here computes authority: every affordance is a server capability.
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../../../../components/field/EffectSurface";
import { AuthorityRelation, ChamberHead, Identifiers, ParticipationRoster, type PersonRelation, ProvenanceSpine, Token } from "../../../../../components/field/chambers";
import { FieldEvent } from "../../../../../components/field/FieldEvent";
import { FieldFrame } from "../../../../../components/field/FieldFrame";
import { ProofDepth } from "../../../../../components/field/ProofDepth";
import { ReadBoundary } from "../../../../../components/field/ReadBoundary";
import { FieldCore, type CoreState } from "../../../../../components/field/topology/FieldCore";
import { FieldStage, Plane, Planes, Topology } from "../../../../../components/field/topology/FieldStage";
import { Orbit, type OrbitNode, nodeContent } from "../../../../../components/field/topology/Orbit";
import { Unavailable } from "../../../../../components/f02/Unavailable";
import { BurstCapturePanel } from "../../../../../components/f03/BurstCapturePanel";
import {
  fetchSessionPosition,
  grantSessionControl,
  type QueryResult,
  runSessionCommand,
  type SessionActionName,
  type SessionPosition,
} from "../../../../../lib/api/inquiryClient";
import type { FieldEventDescription } from "../../../../../lib/field/fieldEvent";
import { humanPosition } from "../../../../../lib/field/humanPosition";
import { accessTrace, sessionTrace } from "../../../../../lib/field/position";
import { lifecycleEmphasis } from "../../../../../lib/field/topology";
import { settleCommand, useEffectField } from "../../../../../lib/field/useEffectField";

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

const STEP_RELATION = "session:step:";
const ADMIT_RELATION = "session:admit-participant";
const GRANT_RELATION = "governance:grant-session-control";

const AT = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });

/** Doc 26 §27: the confirmed effect of each lifecycle step, in human-readable words (scope: this Session). */
const STEP_EVENTS: Readonly<Record<StepAction, FieldEventDescription>> = {
  BEGIN_SETUP: { title: "SETUP BEGUN", text: "This Session entered SETUP. Its method is now being configured." },
  BEGIN_CHALLENGE_CAPTURE: { title: "CHALLENGE CAPTURE BEGUN", text: "This Session entered CHALLENGE_CAPTURE. The Challenge is framed for it." },
  PREPARE_BURST: { title: "PROTECTED BURST PREPARED", text: "A HUMAN_ONLY question burst is prepared for this Session. Nothing is open yet." },
  OPEN_QUESTION_GENERATION: { title: "QUESTION GENERATION OPENED", text: "The protected Burst is open: humans generate questions; AI is absent." },
};

/** The core's identity follows the canonical lifecycle (22 §12.4–§12.6). */
function coreRegime(p: SessionPosition): { readonly state: CoreState; readonly eyebrow: string; readonly regime: "session" | "human-question" | "frozen" } {
  if (p.session.state === "QUESTION_GENERATION" && p.burst?.state === "ACTIVE" && p.burst.mode === "HUMAN_ONLY") {
    return { state: "human", eyebrow: "Human question field · ACTIVE HUMAN_ONLY", regime: "human-question" };
  }
  if (p.burst?.state === "COMPLETED" && p.questionSet.frozen !== null) {
    return { state: "frozen", eyebrow: "Frozen human question set", regime: "frozen" };
  }
  return { state: "current", eyebrow: `Session · ${p.session.method}`, regime: "session" };
}

export default function SessionPage() {
  const { workspaceId, sessionId } = useParams<{ workspaceId: string; sessionId: string }>();
  const router = useRouter();
  const [position, setPosition] = useState<QueryResult<SessionPosition> | null>(null);
  const [participant, setParticipant] = useState("");
  const [grantee, setGrantee] = useState("");
  const effect = useEffectField();
  // descriptions captured at request time (the names the human chose), read only after the confirmed re-read
  const pendingEvents = useRef<Record<string, FieldEventDescription>>({});

  const load = useCallback(
    (): Promise<boolean> =>
      fetchSessionPosition(workspaceId, sessionId).then((result) => {
        if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
          router.replace("/login");
          return false;
        }
        if (result.kind === "network_failure") {
          setPosition((prev) => (prev?.kind === "ok" ? prev : result));
          return false;
        }
        setPosition(result);
        return result.kind === "ok";
      }),
    [workspaceId, sessionId, router],
  );

  useEffect(() => {
    void load();
  }, [load]);

  function runStep(action: Exclude<SessionActionName, "GRANT_SESSION_CONTROL">, extra: { participantUserId?: string } = {}) {
    if (position?.kind !== "ok") return;
    const expectedVersion = position.data.session.version;
    if (action === "ADMIT_PARTICIPANT") {
      const who = position.data.admitCandidates.find((m) => m.userId === extra.participantUserId)?.name ?? "The participant";
      pendingEvents.current[ADMIT_RELATION] = { title: "PARTICIPANT ADMITTED", text: `${who} now takes part in this Session.` };
    }
    void effect.run({
      relation: action === "ADMIT_PARTICIPANT" ? ADMIT_RELATION : `${STEP_RELATION}${action}`,
      keyed: true,
      send: async (intentKey) => {
        const settled = settleCommand(await runSessionCommand(workspaceId, sessionId, action, expectedVersion, intentKey, extra));
        return settled.kind === "stale"
          ? { ...settled, detail: "The Session changed since you loaded it. The re-read state is shown; review it before acting." }
          : settled;
      },
      reconstruct: load,
      onCommitted: () => {
        if (action === "ADMIT_PARTICIPANT") setParticipant("");
        return false;
      },
    });
  }

  function handleGrant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const who = position?.kind === "ok" ? (position.data.grantCandidates.find((m) => m.userId === grantee)?.name ?? "The holder") : "The holder";
    pendingEvents.current[GRANT_RELATION] = { title: "SESSION CONTROL GRANTED", text: `${who} now holds Session control for this Session.` };
    void effect.run({
      relation: GRANT_RELATION,
      keyed: true,
      send: async (intentKey) =>
        settleCommand(await grantSessionControl(workspaceId, grantee, { type: "SESSION", id: sessionId }, intentKey)),
      reconstruct: load,
      onCommitted: () => {
        setGrantee("");
        return false;
      },
    });
  }

  if (position === null) {
    return (
      <FieldFrame trace={accessTrace("established")} regime="session" exit={null}>
        <FieldStage mode="stack" surface="session">
          <FieldCore kind="session" state="loading" eyebrow="Session" title="Reading the Session…" titleAs="p" testId="session-loading" />
        </FieldStage>
      </FieldFrame>
    );
  }
  if (position.kind !== "ok") {
    return (
      <FieldFrame trace={accessTrace("established")} regime="boundary">
        <FieldStage mode="stack" surface="session">
          <FieldCore kind="boundary" state="boundary" eyebrow="Boundary" title="This Session cannot be projected" titleAs="p" stateText={position.kind.toUpperCase()} />
          <ReadBoundary kind={position.kind} reasonCode={position.reasonCode} testId="load-failure" />
        </FieldStage>
      </FieldFrame>
    );
  }
  const p = position.data;
  const admit = p.actions.ADMIT_PARTICIPANT;
  const grantCap = p.actions.GRANT_SESSION_CONTROL;
  const core = coreRegime(p);
  const emphasis = lifecycleEmphasis(p.phases);
  const participantIds = p.participants.map((x) => x.userId);
  const position_ = humanPosition(p.viewer, { scope: "session", participantIds });
  const controllerIds = new Set(p.sessionControllers.map((b) => b.holderUserId));
  const relevantSteps = STEPS.filter((s) => p.actions[s.action].relevant);
  const describeEvent = (relation: string): FieldEventDescription | null => {
    if (relation.startsWith(STEP_RELATION)) return STEP_EVENTS[relation.slice(STEP_RELATION.length) as StepAction] ?? null;
    if (relation.startsWith("session:capture:")) return { title: "QUESTION CAPTURED", text: "Your question is stored exactly as you typed it. Only you can see it while the Burst is open." };
    if (relation === "session:complete-burst") {
      const n = p.questionSet.frozen?.memberCount;
      return { title: "BURST COMPLETED", text: `The human question set is frozen${n !== undefined ? ` (${n} ${n === 1 ? "question" : "questions"})` : ""}. Nothing can be added, removed or rewritten.` };
    }
    return pendingEvents.current[relation] ?? null;
  };

  const lifecycleNodes: OrbitNode[] = p.phases.map((phase, i) => ({
    key: phase.state,
    state: phase.status === "done" ? "established" : phase.status === "current" ? "current" : "future",
    path: phase.status === "done" ? "historical" : phase.status === "current" ? "current" : "dependency",
    // every phase keeps a readable label (doc 23 §13.5); passed/current/next carry the ordinal, later phases a
    // compact name — emphasis is weight, never visibility
    label: emphasis.get(phase.state) === "full" ? `${i + 1}. ${PHASE_LABELS[phase.state] ?? phase.state}` : (PHASE_LABELS[phase.state] ?? phase.state),
    markerText: phase.status === "done" ? "passed" : phase.status === "current" ? "current" : "later",
    size: "sm",
    emphasis: emphasis.get(phase.state),
    ariaCurrent: phase.status === "current" ? "step" : undefined,
  }));
  const relationNodes: OrbitNode[] = [
    ...p.participants.map(
      (x): OrbitNode => ({
        key: `p-${x.userId}`,
        state: "human",
        label: x.name ?? "participant",
        meta: controllerIds.has(x.userId) ? "participant · Session controller" : "participant",
        size: "sm",
      }),
    ),
    ...p.sessionControllers
      .filter((b) => !participantIds.includes(b.holderUserId))
      .map(
        (b): OrbitNode => ({
          key: b.bindingId,
          state: "governance",
          label: b.holderName,
          meta: `Session controller · granted by ${b.grantedByName}`,
          size: "sm",
        }),
      ),
  ];
  if (relationNodes.length === 0) {
    relationNodes.push({ key: "none", state: "unavailable", path: "unavailable", label: "Participation", meta: "no participant and no controller yet", size: "sm" });
  }
  const layoutInput = {
    core: { title: p.challenge.title ?? "Session", stateText: p.session.state, meta: `version ${p.session.version} · ${position_.sentence}` },
    rings: [lifecycleNodes.map((n) => nodeContent(n, "lifecycle")), relationNodes.map((n) => nodeContent(n, "participation"))],
  };
  const phasePlane = core.state === "human" ? "human" : core.state === "frozen" ? "frozen" : "action";

  return (
    <FieldFrame trace={sessionTrace(p)} regime={core.regime}>
      <FieldStage layout={layoutInput} surface="session">
        <Topology layout={layoutInput}>
          <FieldCore
            kind="session"
            state={core.state}
            eyebrow={core.eyebrow}
            title={p.challenge.title ?? "Session"}
            stateText={
              <>
                <span className="visually-hidden">Canonical state: </span>
                <span data-testid="session-state">{p.session.state}</span>
              </>
            }
            meta={
              <>
                version {p.session.version} · {position_.sentence}
                {!p.workspace.governedFounding ? (
                  <>
                    {" "}
                    <span className="tag fixture" data-testid="non-proof-fixture">
                      NON_PROOF fixture
                    </span>
                  </>
                ) : null}
              </>
            }
          >
            <ReconstructionNote field={effect.field} />
          </FieldCore>
          <Orbit kind="lifecycle" ring={1} heading="Lifecycle" nodes={lifecycleNodes} testId="session-phases" listAriaLabel="Session phases" />
          <Orbit kind="participation" ring={2} heading="Participation and control" nodes={relationNodes} testId="session-relations" listAriaLabel="Participants and Session control" />
        </Topology>

        <Planes header={{ eyebrow: "Grown from", title: p.challenge.title ?? "Session", state: p.session.state }}>
          <Plane kind={phasePlane} semantic={core.state === "human" ? "question" : core.state === "frozen" ? "frozen" : "action"} labelledBy="phase-title" testId="active-phase">
            <ChamberHead
              id="phase-title"
              semantic={core.state === "human" ? "question" : core.state === "frozen" ? "frozen" : "action"}
              title={core.state === "human" ? "Protected question burst" : core.state === "frozen" ? "Frozen human question set" : "Active phase"}
              marker={core.state === "human" ? p.burst?.mode : core.state === "frozen" ? "FROZEN" : p.session.state}
            />
            <EffectIntent field={effect.field} relationPrefix="session:" />
            <EffectOutcome field={effect.field} relationPrefix="session:" onReread={() => void effect.rereadNow(load)} />
            {relevantSteps.length > 0 ? (
              <ul className="plain-list" aria-label="Lawful next transitions">
                {relevantSteps.map((s) => {
                  const cap = p.actions[s.action];
                  return (
                    <li key={s.action}>
                      <p style={{ margin: 0 }}>
                        <strong>{s.label}</strong> <span className="muted">— {s.explain}</span>
                      </p>
                      {cap.available ? (
                        <div className="actions-row">
                          <button className="button" type="button" disabled={effect.blocked} onClick={() => runStep(s.action)}>
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
            ) : null}
            {p.burst === null ? (
              <p className="muted" data-testid="burst-absent">
                No burst has been prepared.
              </p>
            ) : (
              <dl className="provenance">
                <dt>Burst</dt>
                <dd>
                  <span className="state" data-testid="burst-state">
                    {p.burst.state}
                  </span>{" "}
                  <span className="tag human" data-testid="burst-mode">
                    {p.burst.mode}
                  </span>{" "}
                  <span className="muted">Only humans author questions. AI is absent while the burst is open.</span>
                </dd>
                {p.burst.state === "ACTIVE" ? (
                  <>
                    <dt>Open since</dt>
                    <dd>{p.burst.startedAt ? AT.format(new Date(p.burst.startedAt)) : "—"}</dd>
                  </>
                ) : null}
                {p.burst.state === "COMPLETED" ? (
                  <>
                    <dt>Completed</dt>
                    <dd>{p.burst.completedAt ? AT.format(new Date(p.burst.completedAt)) : "—"}</dd>
                  </>
                ) : null}
              </dl>
            )}
            <BurstCapturePanel workspaceId={workspaceId} sessionId={sessionId} position={p} effect={effect} reload={load} />
          </Plane>

          <Plane kind="governance" semantic="authority" labelledBy="authority-title">
            <ChamberHead id="authority-title" semantic="authority" title="Session control" marker="SESSION scope" />
            <div data-testid="session-authority-provenance" className="authority-body">
              {p.sessionControllers.length === 0 ? (
                <p className="muted">Nobody holds SESSION_CONTROL_RIGHT for this Session yet.</p>
              ) : (
                <ul className="authority-chain">
                  {p.sessionControllers.map((b) => (
                    <AuthorityRelation
                      key={b.bindingId}
                      bindingKey={b.bindingId}
                      authorityClass={b.authorityClass}
                      holderName={b.holderName}
                      holderKey={participantIds.includes(b.holderUserId) ? `p-${b.holderUserId}` : b.bindingId}
                      grantedByName={b.grantedByName}
                      scope={b.scope}
                      scopeLabel="this Session"
                      held={b.holderUserId === p.viewer.userId}
                    />
                  ))}
                </ul>
              )}
              <p className="human-position">{position_.sentence}</p>
            </div>
            {grantCap.available ? (
              <form onSubmit={handleGrant} className="stack chamber-action">
                <ChamberHead id="gov-title" level={3} semantic="action" title="Grant Session control" marker="for this Session" />
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
                  <button className="button" type="submit" disabled={effect.blocked || grantee === ""}>
                    Grant session control for this Session
                  </button>
                </div>
                <EffectIntent field={effect.field} relationPrefix="governance:" />
                <EffectOutcome field={effect.field} relationPrefix="governance:" onReread={() => void effect.rereadNow(load)} />
              </form>
            ) : null}
          </Plane>

          <Plane kind="governance" semantic="participation" labelledBy="participants-title">
            <ChamberHead id="participants-title" semantic="participation" title="Participants" marker={`${p.participants.length}`} />
            {p.participants.length === 0 ? (
              <p className="muted" data-testid="participants-empty">
                No participant has been admitted yet.
              </p>
            ) : (
              <ParticipationRoster
                testId="participants-list"
                labelledBy="participants-title"
                people={p.participants.map((person) => ({
                  userId: person.userId,
                  name: person.name ?? "participant",
                  relationKey: `p-${person.userId}`,
                  relations: [
                    ...(person.userId === p.viewer.userId ? (["you"] as PersonRelation[]) : []),
                    "participant" as PersonRelation,
                    ...(controllerIds.has(person.userId) ? (["controller"] as PersonRelation[]) : []),
                  ],
                }))}
              />
            )}
            {admit.relevant && admit.available ? (
              <div className="stack chamber-action">
                <ChamberHead id="admit-title" level={3} semantic="action" title="Admit a participant" marker="controller only" />
                <div className="field">
                  <label htmlFor="admit-participant">Admit participant</label>
                  <select id="admit-participant" value={participant} onChange={(e) => setParticipant(e.target.value)}>
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
                  disabled={effect.blocked || participant === ""}
                  onClick={() => runStep("ADMIT_PARTICIPANT", { participantUserId: participant })}
                >
                  Admit to Session
                </button>
              </div>
            ) : admit.relevant ? (
              <Unavailable capability={admit} testId="action-reason-ADMIT_PARTICIPANT" />
            ) : null}
          </Plane>

          <Plane kind="proof" labelledBy="proof-title">
            <ChamberHead id="proof-title" semantic="proof" title="Proof" marker={p.establishedBy ? "governed commit" : "fixture-seeded"} />
            {p.establishedBy ? (
              <ProvenanceSpine
                testId="session-last-transition"
                steps={[
                  { kind: "state", label: "Current state", value: p.session.state },
                  {
                    kind: "actor",
                    label: "Established by",
                    value: (
                      <>
                        <span className="mono">{p.establishedBy.commandType}</span> by {p.establishedBy.actorName ?? "unknown"}
                      </>
                    ),
                  },
                  {
                    kind: "authority",
                    label: "Authority source",
                    value: (
                      <>
                        {p.establishedBy.authoritySourceType ?? "untyped (pre-F02)"}{" "}
                        {p.establishedBy.authorityScopeRef ? <Token value={p.establishedBy.authorityScopeRef} /> : null}
                      </>
                    ),
                  },
                  { kind: "commit", label: "Commit", value: <Token value={p.establishedBy.commitId} /> },
                  { kind: "time", label: "At", value: AT.format(new Date(p.establishedBy.occurredAt)) },
                ]}
              />
            ) : (
              <p className="muted" data-testid="session-last-transition">
                No governed commit established this state (fixture-seeded).
              </p>
            )}
            <ProofDepth depth="D3" title="Identifiers" testId="session-identifiers">
              <Identifiers
                items={[
                  { label: "Session", value: p.session.sessionId },
                  { label: "Challenge", value: p.challenge.challengeId },
                  ...(p.burst ? [{ label: "Burst", value: `${p.burst.burstId} · version ${p.burst.version}` }] : []),
                ]}
              />
            </ProofDepth>
          </Plane>

          <Plane kind="context" semantic="decision-entry" labelledBy="decision-entry-title">
            <ChamberHead id="decision-entry-title" semantic="decision-entry" title="Decision surface" marker="NON_PROOF" />
            <p className="chamber-lede">
              <Link href={`/workspaces/${workspaceId}/sessions/${sessionId}/decision`}>Enter the Decision surface</Link> — PKG-29 prototype view; it records
              a human Decision under its own authority check and proves nothing about this Session beyond what the server returns.
            </p>
          </Plane>
        </Planes>
        <FieldEvent field={effect.field} describe={describeEvent} />
      </FieldStage>
    </FieldFrame>
  );
}
