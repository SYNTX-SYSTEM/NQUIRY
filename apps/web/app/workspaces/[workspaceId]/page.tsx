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
 */
import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "../../../components/f02/AppShell";
import { Outcome, type ShownOutcome } from "../../../components/f02/Outcome";
import { Unavailable } from "../../../components/f02/Unavailable";
import { fetchCurrentSession } from "../../../lib/api/authClient";
import {
  addMemberCommand,
  createChallenge,
  fetchWorkspaceOverview,
  newIntentKey,
  type QueryResult,
  type WorkspaceOverview,
} from "../../../lib/api/inquiryClient";
import { fetchWorkspaceOrientation, type WorkspaceOrientationResult } from "../../../lib/api/workspaceClient";

type Orientation = { readonly kind: "checking" } | { readonly kind: "loaded"; readonly result: WorkspaceOrientationResult } | { readonly kind: "error" };

export default function WorkspacePage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const router = useRouter();
  const [orientation, setOrientation] = useState<Orientation>({ kind: "checking" });
  const [overview, setOverview] = useState<QueryResult<WorkspaceOverview> | null>(null);
  const [memberId, setMemberId] = useState("");
  const [memberRole, setMemberRole] = useState("Contributor");
  const [memberBusy, setMemberBusy] = useState(false);
  const [memberResult, setMemberResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [challengeIntent, setChallengeIntent] = useState(newIntentKey);
  const [challengeBusy, setChallengeBusy] = useState(false);
  const [outcome, setOutcome] = useState<ShownOutcome | null>(null);

  const load = useCallback(() => {
    fetchWorkspaceOrientation(workspaceId)
      .then((result) => setOrientation({ kind: "loaded", result }))
      .catch(() => setOrientation({ kind: "error" }));
    fetchWorkspaceOverview(workspaceId).then((result) => {
      if (result.kind === "denied" && result.reasonCode === "NO_VALID_SESSION") {
        router.replace("/login");
        return;
      }
      setOverview(result);
    });
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
        load();
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
    setMemberBusy(true);
    setMemberResult(null);
    addMemberCommand(workspaceId, memberId.trim(), memberRole).then((result) => {
      setMemberBusy(false);
      if (result.kind === "committed") {
        setMemberResult({ ok: true, message: "Member added." });
        setOutcome({ kind: "committed" });
        setMemberId("");
        load();
        return;
      }
      setMemberResult({ ok: false, message: result.reasonCode });
      setOutcome(result);
    });
  }

  function handleCreateChallenge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setChallengeBusy(true);
    createChallenge(workspaceId, { title, description }, challengeIntent).then((result) => {
      setChallengeBusy(false);
      if (result.kind === "committed") {
        setChallengeIntent(newIntentKey());
        router.push(`/workspaces/${workspaceId}/challenges/${result.body.challengeId}`);
        return;
      }
      if (result.kind !== "network_failure") {
        // A server verdict ends this intent; a new submission is a new intent.
        setChallengeIntent(newIntentKey());
      }
      setOutcome(result);
    });
  }

  const name =
    overview?.kind === "ok"
      ? overview.data.workspace.name
      : orientation.kind === "loaded" && orientation.result.kind === "ok"
        ? orientation.result.workspace.name
        : "Workspace";

  return (
    <AppShell crumbs={[{ label: "Workspaces", href: "/workspaces" }, { label: name }]}>
      {orientation.kind === "checking" ? <p data-testid="orientation-checking">Loading Workspace…</p> : null}
      {orientation.kind === "error" ? (
        <p role="alert" data-testid="orientation-error">
          Unable to reach the server. Please try again.
        </p>
      ) : null}
      {orientation.kind === "loaded" && orientation.result.kind === "rejected" ? (
        // F02 WU-02.12 (FBR-C): a malformed Workspace id is rejected input, not a denial.
        <p role="alert" data-testid="orientation-rejected">
          Rejected: this address does not name a valid Workspace ({orientation.result.reasonCode}).
        </p>
      ) : null}
      {orientation.kind === "loaded" && orientation.result.kind === "denied" ? (
        <p role="alert" data-testid="orientation-denied">
          {orientation.result.reasonCode}
        </p>
      ) : null}

      {orientation.kind === "loaded" && orientation.result.kind === "ok" ? (
        <div className="stack">
          <header>
            <p className="eyebrow">Workspace</p>
            <h1 data-testid="orientation-workspace-name">{orientation.result.workspace.name}</h1>
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

          <Outcome outcome={outcome} />

          <div className="grid-2">
            <section className="panel" aria-labelledby="challenges-title">
              <h2 id="challenges-title">Challenges</h2>
              {overview === null ? <p className="muted">Loading Challenges…</p> : null}
              {overview !== null && overview.kind !== "ok" ? <Outcome outcome={overview} /> : null}
              {overview?.kind === "ok" ? (
                <>
                  {overview.data.challenges.length === 0 ? (
                    <p className="muted" data-testid="challenges-empty">
                      No Challenge has been framed in this Workspace yet.
                    </p>
                  ) : (
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
                  )}
                  {overview.data.capabilities.createChallenge.available ? (
                    <form onSubmit={handleCreateChallenge} data-testid="create-challenge-form" className="stack">
                      <h3>Frame a new Challenge</h3>
                      <div className="field">
                        <label htmlFor="challenge-title">Challenge title</label>
                        <input
                          id="challenge-title"
                          required
                          value={title}
                          onChange={(e) => setTitle(e.target.value)}
                        />
                      </div>
                      <div className="field">
                        <label htmlFor="challenge-description">Description</label>
                        <textarea
                          id="challenge-description"
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                        />
                      </div>
                      <button className="button" type="submit" disabled={challengeBusy}>
                        {challengeBusy ? "Creating…" : "Create Challenge"}
                      </button>
                    </form>
                  ) : (
                    <Unavailable
                      capability={overview.data.capabilities.createChallenge}
                      testId="challenge-create-unavailable"
                    />
                  )}
                </>
              ) : null}
            </section>

            <aside className="stack" aria-label="Membership and authority">
              <section className="panel">
                <h2>You in this Workspace</h2>
                <p data-testid="orientation-role">Your role: {orientation.result.role}</p>
                <p data-testid="orientation-authorized">Authorized: {String(orientation.result.authorized)}</p>
                <p data-testid="orientation-governance-capable">
                  Governance-capable: {String(orientation.result.governanceCapable)}
                </p>
                {orientation.result.heldAuthorityClasses.length > 0 ? (
                  <ul data-testid="orientation-authority-classes" className="plain-list">
                    {orientation.result.heldAuthorityClasses.map((c) => (
                      <li key={c}>
                        <span className="tag authority">{c}</span>
                      </li>
                    ))}
                  </ul>
                ) : null}
                <p className="muted">A role is not authority. Actions need a current, scoped binding.</p>
              </section>

              {overview?.kind === "ok" ? (
                <section className="panel" aria-labelledby="members-title">
                  <h2 id="members-title">Members</h2>
                  <ul className="plain-list" data-testid="members-list">
                    {overview.data.members.map((m) => (
                      <li key={m.userId}>
                        <strong>{m.name}</strong> <span className="muted">· {m.role ?? "no role"}</span>
                        <div className="mono muted">{m.userId}</div>
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}

              {orientation.result.governanceCapable ? (
                <section className="panel">
                  <h2>Add a member</h2>
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
                      <button className="button" type="submit" data-testid="add-member-submit" disabled={memberBusy}>
                        {memberBusy ? "Adding…" : "Add member"}
                      </button>
                    </div>
                  </form>
                  {memberResult?.ok ? <p data-testid="add-member-success">{memberResult.message}</p> : null}
                  {memberResult && !memberResult.ok ? (
                    <p role="alert" data-testid="add-member-error">
                      {memberResult.message}
                    </p>
                  ) : null}
                </section>
              ) : null}
            </aside>
          </div>
        </div>
      ) : null}
    </AppShell>
  );
}
