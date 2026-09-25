"use client";
/**
 * Workspace Field (22 §22.2): Core = the Workspace; orbits = its Challenges
 * (containment, with the "Frame a Challenge" relation first, possible or
 * unavailable from the server capability) and its members (participation) with
 * the viewer's own authority relations (governance); planes = instruments.
 *
 * F01's orientation contract (`GET /workspaces/{w}`: role, held authority
 * classes, authorized, governanceCapable; test ids `orientation-*`,
 * `add-member-*`) and F02's overview (`GET /workspaces/{w}/overview`: members,
 * Challenges, `createChallenge` / `addMember` capabilities) are the only sources.
 * Nothing here decides authority: the add-member form appears only when the
 * server projects the viewer governance-capable; the Challenge form only when
 * `createChallenge` is available; otherwise the server's own reason is shown.
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../../components/field/EffectSurface";
import { ChamberHead, Identifiers, ParticipationRoster, type PersonRelation, roleRelation } from "../../../components/field/chambers";
import { FieldEvent } from "../../../components/field/FieldEvent";
import { FieldFrame } from "../../../components/field/FieldFrame";
import { ProofDepth } from "../../../components/field/ProofDepth";
import { ReadBoundary } from "../../../components/field/ReadBoundary";
import { FieldCore } from "../../../components/field/topology/FieldCore";
import { FieldStage, Plane, Planes, Topology } from "../../../components/field/topology/FieldStage";
import { Orbit, type OrbitNode, nodeContent } from "../../../components/field/topology/Orbit";
import { Unavailable } from "../../../components/f02/Unavailable";
import { fetchCurrentSession } from "../../../lib/api/authClient";
import {
  addMemberCommand,
  createChallenge,
  fetchWorkspaceOverview,
  type QueryResult,
  type WorkspaceOverview,
} from "../../../lib/api/inquiryClient";
import { fetchWorkspaceOrientation, type WorkspaceOrientationResult } from "../../../lib/api/workspaceClient";
import type { FieldEventDescription } from "../../../lib/field/fieldEvent";
import { humanPosition } from "../../../lib/field/humanPosition";
import { accessTrace, workspaceNameTrace, workspaceTrace } from "../../../lib/field/position";
import { affordanceState } from "../../../lib/field/topology";
import { settleCommand, useEffectField } from "../../../lib/field/useEffectField";

type Orientation = { readonly kind: "checking" } | { readonly kind: "loaded"; readonly result: WorkspaceOrientationResult } | { readonly kind: "error" };

const CREATE_CHALLENGE = "create-challenge";
const ADD_MEMBER = "add-member";

export default function WorkspacePage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const router = useRouter();
  const [orientation, setOrientation] = useState<Orientation>({ kind: "checking" });
  const [overview, setOverview] = useState<QueryResult<WorkspaceOverview> | null>(null);
  const [memberId, setMemberId] = useState("");
  const [memberRole, setMemberRole] = useState("Contributor");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const effect = useEffectField();
  const pendingEvents = useRef<Record<string, FieldEventDescription>>({});

  /** Canonical re-read of both projections. True only if both are current. */
  const load = useCallback(async (): Promise<boolean> => {
    const [orientationOk, overviewOk] = await Promise.all([
      fetchWorkspaceOrientation(workspaceId)
        .then((result) => {
          setOrientation({ kind: "loaded", result });
          return result.kind === "ok";
        })
        .catch(() => {
          setOrientation((prev) => (prev.kind === "loaded" && prev.result.kind === "ok" ? prev : { kind: "error" }));
          return false;
        }),
      fetchWorkspaceOverview(workspaceId).then((result) => {
        if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
          router.replace("/login");
          return false;
        }
        if (result.kind === "network_failure") {
          setOverview((prev) => (prev?.kind === "ok" ? prev : result));
          return false;
        }
        setOverview(result);
        return result.kind === "ok";
      }),
    ]);
    return orientationOk && overviewOk;
  }, [workspaceId, router]);

  useEffect(() => {
    let cancelled = false;
    fetchCurrentSession()
      .then((session) => {
        if (cancelled) return;
        if (session.kind !== "ok") {
          router.replace("/login");
          return;
        }
        void load();
      })
      .catch(() => {
        if (!cancelled) router.replace("/login");
      });
    return () => {
      cancelled = true;
    };
  }, [router, load]);

  function handleAddMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    pendingEvents.current[ADD_MEMBER] = {
      title: "MEMBER ADDED",
      text: `${memberId.trim().slice(0, 8)}… now holds membership in this Workspace with the ${memberRole} role. Membership grants no authority.`,
    };
    void effect.run({
      relation: ADD_MEMBER,
      keyed: false,
      send: async () => settleCommand(await addMemberCommand(workspaceId, memberId.trim(), memberRole)),
      reconstruct: load,
      onCommitted: () => {
        setMemberId("");
        return false;
      },
    });
  }

  function handleCreateChallenge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void effect.run({
      relation: CREATE_CHALLENGE,
      keyed: true,
      send: async (intentKey) => settleCommand(await createChallenge(workspaceId, { title, description }, intentKey)),
      reconstruct: load,
      onCommitted: (body) => {
        router.push(`/workspaces/${workspaceId}/challenges/${body.challengeId}`);
        return true;
      },
    });
  }

  const confirmed = orientation.kind === "loaded" && orientation.result.kind === "ok" ? orientation.result : null;
  const ov = overview?.kind === "ok" ? overview.data : null;
  const trace = ov ? workspaceTrace(ov) : confirmed ? workspaceNameTrace(confirmed.workspace.name) : accessTrace("established");

  if (!confirmed) {
    const boundary =
      orientation.kind === "error" ? (
        <ReadBoundary kind="network_failure" reasonCode="NETWORK_FAILURE" testId="orientation-error" />
      ) : orientation.kind === "loaded" && orientation.result.kind === "rejected" ? (
        <ReadBoundary kind="rejected" reasonCode={orientation.result.reasonCode} testId="orientation-rejected" />
      ) : orientation.kind === "loaded" && orientation.result.kind === "denied" ? (
        <ReadBoundary kind="denied" reasonCode={orientation.result.reasonCode} reasonTestId="orientation-denied" />
      ) : null;
    return (
      <FieldFrame trace={trace} regime={boundary ? "boundary" : "workspace"} exit={boundary ? undefined : null}>
        <FieldStage mode="stack" surface="workspace">
          {boundary ? (
            <>
              <FieldCore kind="boundary" state="boundary" eyebrow="Boundary" title="This Workspace cannot be projected" titleAs="p" stateText={orientation.kind === "loaded" ? orientation.result.kind.toUpperCase() : "NETWORK_FAILURE"} />
              {boundary}
            </>
          ) : (
            <FieldCore kind="workspace" state="loading" eyebrow="Workspace" title="Reading the Workspace…" titleAs="p" testId="orientation-checking" />
          )}
        </FieldStage>
      </FieldFrame>
    );
  }

  const frameCap = ov?.capabilities.createChallenge ?? null;
  const challengeNodes: OrbitNode[] = ov
    ? [
        {
          key: "frame",
          state: affordanceState(frameCap!),
          label: "New Challenge",
          actionLabel: "Frame a new Challenge",
          onActivate: frameCap!.available ? () => document.getElementById("challenge-title")?.focus() : undefined,
          meta: frameCap!.available ? "possible next relation" : "not available now",
          describedBy: frameCap!.available ? undefined : "challenge-create-unavailable",
          testId: "new-challenge-node",
        },
        ...ov.challenges.map(
          (c): OrbitNode => ({
            key: c.challengeId,
            state: "established",
            label: c.title,
            meta: "Challenge",
            href: `/workspaces/${workspaceId}/challenges/${c.challengeId}`,
          }),
        ),
      ]
    : [];
  const memberNodes: OrbitNode[] = ov
    ? [
        ...confirmed.heldAuthorityClasses.map(
          (c): OrbitNode => ({ key: `auth-${c}`, state: "governance", label: "You hold", meta: c, size: "sm" }),
        ),
        ...ov.members.map(
          (m): OrbitNode => ({ key: m.userId, state: "human", label: m.name, meta: m.role ?? "no role", size: "sm" }),
        ),
      ]
    : [];
  const position = humanPosition({ userId: ov?.viewer.userId ?? "", role: confirmed.role, governanceCapable: confirmed.governanceCapable }, { scope: "workspace" });
  const layoutInput = {
    core: { title: confirmed.workspace.name, stateText: ov ? `${ov.challenges.length} Challenges · ${ov.members.length} members` : "reading…", meta: position.relations.join(" · ") },
    rings: ov ? [challengeNodes.map((n) => nodeContent(n, "containment")), memberNodes.map((n) => nodeContent(n, "participation"))] : [],
  };

  return (
    <FieldFrame trace={trace} regime="workspace">
      <FieldStage layout={ov ? layoutInput : undefined} mode={ov ? undefined : "stack"} surface="workspace">
        <Topology layout={layoutInput}>
          <FieldCore
            kind="workspace"
            state="current"
            eyebrow="Workspace"
            title={<span data-testid="orientation-workspace-name">{confirmed.workspace.name}</span>}
            stateText={ov ? `${ov.challenges.length} ${ov.challenges.length === 1 ? "Challenge" : "Challenges"} · ${ov.members.length} ${ov.members.length === 1 ? "member" : "members"}` : "reading…"}
            meta={position.relations.join(" · ")}
          >
            <ReconstructionNote field={effect.field} />
          </FieldCore>
          {ov ? (
            <>
              <Orbit kind="containment" ring={1} heading="Challenges" nodes={challengeNodes} testId="challenges-list" listAriaLabel="Challenges of this Workspace" />
              <Orbit kind="participation" ring={2} heading="Members and authority" nodes={memberNodes} testId="members-orbit" listAriaLabel="Members and your authority in this Workspace" />
            </>
          ) : null}
        </Topology>

        <Planes header={{ eyebrow: "Grown from", title: confirmed.workspace.name, state: ov ? `${ov.challenges.length} ${ov.challenges.length === 1 ? "Challenge" : "Challenges"} · ${ov.members.length} ${ov.members.length === 1 ? "member" : "members"}` : "reading…" }}>
          <Plane kind="action" labelledBy="frame-challenge-title">
            <ChamberHead id="frame-challenge-title" semantic="action" title="Frame a new Challenge" marker={ov ? (frameCap!.available ? "possible" : "not possible now") : undefined} />
            {overview === null ? <p className="projection-pending">Reading Challenges…</p> : null}
            {overview !== null && overview.kind !== "ok" ? <ReadBoundary kind={overview.kind} reasonCode={overview.reasonCode} /> : null}
            {ov && ov.challenges.length === 0 ? (
              <p className="muted" data-testid="challenges-empty">
                No Challenge has been framed in this Workspace yet.
              </p>
            ) : null}
            {ov && !ov.workspace.governedFounding ? (
              <p>
                <span className="tag fixture" data-testid="non-proof-fixture">
                  NON_PROOF fixture
                </span>{" "}
                <span className="muted">This Workspace was seeded by a development fixture, not founded through the governed founding Command.</span>
              </p>
            ) : null}
            {ov ? (
              frameCap!.available ? (
                <form onSubmit={handleCreateChallenge} data-testid="create-challenge-form" className="stack">
                  <div className="field">
                    <label htmlFor="challenge-title">Challenge title</label>
                    <input id="challenge-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
                  </div>
                  <div className="field">
                    <label htmlFor="challenge-description">Description</label>
                    <textarea id="challenge-description" value={description} onChange={(e) => setDescription(e.target.value)} />
                  </div>
                  <button className="button" type="submit" disabled={effect.blocked}>
                    Create Challenge
                  </button>
                </form>
              ) : (
                <Unavailable capability={frameCap!} testId="challenge-create-unavailable" />
              )
            ) : null}
            <EffectIntent field={effect.field} relation={CREATE_CHALLENGE} />
            <EffectOutcome field={effect.field} relation={CREATE_CHALLENGE} onReread={() => void effect.rereadNow(load)} />
          </Plane>

          <Plane kind="governance" semantic="identity" labelledBy="standing-title">
            <ChamberHead id="standing-title" semantic="identity" title="You in this Workspace" marker={confirmed.role} />
            <ul className="identity-facts">
              <li data-testid="orientation-role">Your role: {confirmed.role}</li>
              <li data-testid="orientation-authorized">Authorized: {String(confirmed.authorized)}</li>
              <li data-testid="orientation-governance-capable">Governance-capable: {String(confirmed.governanceCapable)}</li>
            </ul>
            <p className="chamber-lede">A role is not authority. Actions need a current, scoped binding.</p>
          </Plane>

          <Plane kind="governance" semantic="participation" labelledBy="members-title">
            <ChamberHead id="members-title" semantic="participation" title="Members" marker={ov ? `${ov.members.length}` : undefined} />
            {ov ? (
              <ParticipationRoster
                testId="members-list"
                labelledBy="members-title"
                people={ov.members.map((m) => ({
                  userId: m.userId,
                  name: m.name,
                  relationKey: m.userId,
                  relations: [
                    ...(m.userId === ov.viewer.userId ? (["you"] as PersonRelation[]) : []),
                    roleRelation(m.role),
                  ],
                }))}
              />
            ) : null}
            {confirmed.governanceCapable ? (
              <>
                <ChamberHead id="add-member-title" level={3} semantic="action" title="Add a member" marker="governance root" />
                <p className="muted">Governance root only. Adds membership and a role. It grants no authority.</p>
                <form onSubmit={handleAddMember} data-testid="add-member-form">
                  <div className="field">
                    <label htmlFor="new-member-user-id">Member user id</label>
                    <input
                      id="new-member-user-id"
                      data-testid="new-member-user-id-input"
                      type="text"
                      required
                      value={memberId}
                      onChange={(e) => setMemberId(e.target.value)}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="new-member-role">Role</label>
                    <select id="new-member-role" data-testid="new-member-role-select" value={memberRole} onChange={(e) => setMemberRole(e.target.value)}>
                      <option value="Contributor">Contributor</option>
                      <option value="Facilitator">Facilitator</option>
                    </select>
                  </div>
                  <div className="actions-row">
                    <button className="button" type="submit" data-testid="add-member-submit" disabled={effect.blocked}>
                      Add member
                    </button>
                  </div>
                </form>
                <EffectIntent field={effect.field} relation={ADD_MEMBER} />
                <EffectOutcome
                  field={effect.field}
                  relation={ADD_MEMBER}
                  reasonTestId="add-member-error"
                  committedTestId="add-member-success"
                  onReread={() => void effect.rereadNow(load)}
                />
              </>
            ) : null}
          </Plane>

          <Plane kind="proof" semantic="authority" labelledBy="workspace-authority-title">
            <ChamberHead id="workspace-authority-title" semantic="authority" title="Authority you hold here" marker="scoped bindings" />
            <ProofDepth depth="D2" title="Authority you hold here" testId="workspace-authority-proof">
              {confirmed.heldAuthorityClasses.length > 0 ? (
                <ul data-testid="orientation-authority-classes" className="plain-list">
                  {confirmed.heldAuthorityClasses.map((c) => (
                    <li key={c}>
                      <span className="tag authority">{c}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>You hold no authority binding in this Workspace.</p>
              )}
            </ProofDepth>
            <ChamberHead id="workspace-ids-title" level={3} semantic="identifiers" title="Identifiers" />
            <Identifiers items={[{ label: "Workspace", value: confirmed.workspace.workspaceId }, { label: "You", value: ov?.viewer.userId ?? confirmed.workspace.ownerId }]} />
            <p className="muted">
              <Link href="/workspaces">All accessible Workspaces</Link>
            </p>
          </Plane>
        </Planes>
        <FieldEvent field={effect.field} describe={(relation) => pendingEvents.current[relation] ?? null} />
      </FieldStage>
    </FieldFrame>
  );
}
