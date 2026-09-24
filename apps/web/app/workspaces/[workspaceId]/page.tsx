"use client";
/**
 * Workspace page (F01 orientation + F02 inquiry entry, WU-02.10).
 *
 * F01's orientation contract (`GET /workspaces/{w}`, testids `orientation-*`,
 * `add-member-*`) is preserved. F02 adds the Workspace overview
 * (`GET /workspaces/{w}/overview`): members, Challenges, and the server's
 * capability to create a Challenge (AUTH-DEP-CH-001, Facilitator role).
 *
 * Nothing here decides authority. The add-member form appears only when
 * the server says the viewer is governance-capable. The Challenge form
 * appears only when the server's `createChallenge` capability is available;
 * otherwise the server's own reason is shown in its place.
 *
 * SF-01 (21 CF-01/CF-02/CF-07/CF-08/CF-09): the Workspace regime of the
 * Relational Interaction Field.
 * - Position: Relation Trace from the confirmed projection only (overview,
 *   else the F01 orientation name, else the access context).
 * - Centre: the Challenges (problem contexts). Near: framing a Challenge and
 *   adding a member, each one effect relation with its own intent, outcome and
 *   re-read. Outer: who the viewer is here, and the members. Depth (D2): the
 *   authority classes the viewer holds.
 * - A re-read that fails keeps the last confirmed projection, explicitly
 *   marked, instead of replacing it or pretending it is current.
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { EffectIntent, EffectOutcome, ReconstructionNote } from "../../../components/field/EffectSurface";
import { FieldFrame, FieldLayout, FieldZone } from "../../../components/field/FieldFrame";
import { ProofDepth } from "../../../components/field/ProofDepth";
import { ReadBoundary } from "../../../components/field/ReadBoundary";
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
import { accessTrace, workspaceNameTrace, workspaceTrace } from "../../../lib/field/position";
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

  /** Canonical re-read of both projections. True only if both are current. */
  const load = useCallback(async (): Promise<boolean> => {
    const [orientationOk, overviewOk] = await Promise.all([
      fetchWorkspaceOrientation(workspaceId)
        .then((result) => {
          setOrientation({ kind: "loaded", result });
          return result.kind === "ok";
        })
        .catch(() => {
          // A confirmed orientation stays, marked last confirmed by ReconstructionNote.
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
    void effect.run({
      relation: ADD_MEMBER,
      // F01 route: no Idempotency-Key in its contract (F02 FIELD_REVIEW known limitation).
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
  const trace =
    overview?.kind === "ok"
      ? workspaceTrace(overview.data)
      : confirmed
        ? workspaceNameTrace(confirmed.workspace.name)
        : accessTrace("established");

  return (
    <FieldFrame trace={trace} regime="workspace">
      {orientation.kind === "checking" ? <p data-testid="orientation-checking">Loading Workspace…</p> : null}
      {orientation.kind === "error" ? (
        <ReadBoundary kind="network_failure" reasonCode="NETWORK_FAILURE" testId="orientation-error" />
      ) : null}
      {orientation.kind === "loaded" && orientation.result.kind === "rejected" ? (
        <ReadBoundary kind="rejected" reasonCode={orientation.result.reasonCode} testId="orientation-rejected" />
      ) : null}
      {orientation.kind === "loaded" && orientation.result.kind === "denied" ? (
        <ReadBoundary kind="denied" reasonCode={orientation.result.reasonCode} reasonTestId="orientation-denied" />
      ) : null}

      {confirmed ? (
        <>
          <header className="field-heading">
            <p className="eyebrow">Workspace</p>
            <h1 data-testid="orientation-workspace-name">{confirmed.workspace.name}</h1>
            {overview?.kind === "ok" && !overview.data.workspace.governedFounding ? (
              <p>
                <span className="tag fixture" data-testid="non-proof-fixture">
                  NON_PROOF fixture
                </span>{" "}
                <span className="muted">
                  This Workspace was seeded by a development fixture, not founded through the governed founding Command.
                </span>
              </p>
            ) : null}
          </header>

          <FieldLayout
            primary={
              <>
                <FieldZone zone="centre" labelledBy="challenges-title">
                  <ReconstructionNote field={effect.field} />
                  <h2 id="challenges-title">Challenges</h2>
                  {overview === null ? <p className="muted">Loading Challenges…</p> : null}
                  {overview !== null && overview.kind !== "ok" ? (
                    <ReadBoundary kind={overview.kind} reasonCode={overview.reasonCode} />
                  ) : null}
                  {overview?.kind === "ok" && overview.data.challenges.length === 0 ? (
                    <p className="muted" data-testid="challenges-empty">
                      No Challenge has been framed in this Workspace yet.
                    </p>
                  ) : null}
                  {overview?.kind === "ok" && overview.data.challenges.length > 0 ? (
                    <ul className="plain-list" data-testid="challenges-list">
                      {overview.data.challenges.map((c) => (
                        <li key={c.challengeId}>
                          <Link className="card-link" href={`/workspaces/${workspaceId}/challenges/${c.challengeId}`}>
                            {c.title}
                          </Link>
                          {c.description ? <p className="muted">{c.description}</p> : null}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </FieldZone>

                {overview?.kind === "ok" ? (
                  <FieldZone zone="near" labelledBy="frame-challenge-title">
                    <h2 id="frame-challenge-title">Frame a new Challenge</h2>
                    {overview.data.capabilities.createChallenge.available ? (
                      <form onSubmit={handleCreateChallenge} data-testid="create-challenge-form" className="stack">
                        <div className="field">
                          <label htmlFor="challenge-title">Challenge title</label>
                          <input id="challenge-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
                        </div>
                        <div className="field">
                          <label htmlFor="challenge-description">Description</label>
                          <textarea
                            id="challenge-description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                          />
                        </div>
                        <button className="button" type="submit" disabled={effect.blocked}>
                          Create Challenge
                        </button>
                      </form>
                    ) : (
                      <Unavailable
                        capability={overview.data.capabilities.createChallenge}
                        testId="challenge-create-unavailable"
                      />
                    )}
                    <EffectIntent field={effect.field} relation={CREATE_CHALLENGE} />
                    <EffectOutcome
                      field={effect.field}
                      relation={CREATE_CHALLENGE}
                      onReread={() => void effect.rereadNow(load)}
                    />
                  </FieldZone>
                ) : null}

                {confirmed.governanceCapable ? (
                  <FieldZone zone="near" labelledBy="add-member-title">
                    <h2 id="add-member-title">Add a member</h2>
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
                        <select
                          id="new-member-role"
                          data-testid="new-member-role-select"
                          value={memberRole}
                          onChange={(e) => setMemberRole(e.target.value)}
                        >
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
                  </FieldZone>
                ) : null}
              </>
            }
            secondary={
              <>
                <FieldZone zone="outer" labelledBy="standing-title">
                  <h2 id="standing-title">You in this Workspace</h2>
                  <p data-testid="orientation-role">Your role: {confirmed.role}</p>
                  <p data-testid="orientation-authorized">Authorized: {String(confirmed.authorized)}</p>
                  <p data-testid="orientation-governance-capable">
                    Governance-capable: {String(confirmed.governanceCapable)}
                  </p>
                  <p className="muted">A role is not authority. Actions need a current, scoped binding.</p>
                  {overview?.kind === "ok" ? (
                    <>
                      <h3 id="members-title">Members</h3>
                      <ul className="plain-list" data-testid="members-list" aria-labelledby="members-title">
                        {overview.data.members.map((m) => (
                          <li key={m.userId}>
                            <strong>{m.name}</strong> <span className="muted">· {m.role ?? "no role"}</span>
                            <div className="t-proof muted">{m.userId}</div>
                          </li>
                        ))}
                      </ul>
                    </>
                  ) : null}
                </FieldZone>
                <FieldZone zone="depth" label="Authority proof for this Workspace">
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
                </FieldZone>
              </>
            }
          />
        </>
      ) : null}
    </FieldFrame>
  );
}
