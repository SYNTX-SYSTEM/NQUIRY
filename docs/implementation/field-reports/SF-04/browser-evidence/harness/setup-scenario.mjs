/**
 * SF-03 review scenario setup (evidence tool; not a product test). Establishes, THROUGH THE PRODUCT'S OWN COMMANDS
 * (real API, real authority checks), the relations the review harness reads:
 *
 *   owner founds a Workspace → owner adds the facilitator (Facilitator) → facilitator frames a Challenge →
 *   owner grants SESSION_CONTROL_RIGHT at CHALLENGE scope to the facilitator.
 *
 * Run twice: once with review names, once with STRESS names (doc 23 §6 typography stress: 104-character Workspace
 * name, 150-character Challenge title). Identities must already exist (HD-3 DEV-ONLY provisioning, see
 * FRONTEND_BROWSER_REVIEW.md §2). Prints `WS=<id> CH=<id>` for the harness.
 *
 * Usage (runtime up):  node setup-scenario.mjs [--stress]   (INSPECT_BASE defaults to http://127.0.0.1:13400)
 */
import { randomUUID } from "node:crypto";

const BASE = process.env.INSPECT_BASE ?? "http://127.0.0.1:13400";
const stress = process.argv.includes("--stress");
const NAMES = stress
  ? {
      workspace: "Cross-Functional Customer Activation and Retention Inquiry Workspace for the European Enterprise Segment",
      challenge: "Why did activation stall after onboarding for enterprise customers who purchased through partners in the last two quarters, and what did we assume?",
      description: "Understand the drop before deciding what to change. Partners, onboarding, expectations, evidence.",
    }
  : { workspace: "SF-03 Inspection", challenge: "Why did activation stall after onboarding?", description: "Understand the drop before deciding what to change." };
const ID = {
  owner: { email: "owner@inspect.local.test", password: "inspect-owner-2026" },
  facilitator: { email: "facilitator@inspect.local.test", password: "inspect-fac-2026" },
};

async function session(who) {
  const r = await fetch(`${BASE}/api/auth/login`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(who) });
  const cookie = r.headers.get("set-cookie")?.split(";")[0];
  const me = await r.json();
  if (!cookie || me.kind !== "ok") throw new Error(`login failed for ${who.email}: ${JSON.stringify(me)}`);
  const call = async (method, path, body, keyed = false) => {
    const res = await fetch(`${BASE}/api${path}`, {
      method,
      headers: { "content-type": "application/json", accept: "application/json", cookie, ...(keyed ? { "Idempotency-Key": randomUUID() } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const json = await res.json().catch(() => ({}));
    return { status: res.status, body: json };
  };
  return { userId: me.userId, call };
}

const owner = await session(ID.owner);
const facilitator = await session(ID.facilitator);

const founded = await owner.call("POST", "/workspaces", { name: NAMES.workspace });
if (founded.body.kind !== "committed" && founded.body.kind !== "ok") throw new Error(`founding: ${JSON.stringify(founded)}`);
const WS = founded.body.workspaceId ?? founded.body.body?.workspaceId;
const member = await owner.call("POST", `/workspaces/${WS}/members`, { userId: facilitator.userId, role: "Facilitator" });
if (!/committed|ok/.test(member.body.kind ?? "")) throw new Error(`add member: ${JSON.stringify(member)}`);
const framed = await facilitator.call("POST", `/workspaces/${WS}/challenges`, { title: NAMES.challenge, description: NAMES.description }, true);
if (framed.body.kind !== "committed") throw new Error(`frame: ${JSON.stringify(framed)}`);
const CH = framed.body.challengeId ?? framed.body.body?.challengeId;
const grant = await owner.call("POST", `/workspaces/${WS}/authority-bindings`, { humanUserId: facilitator.userId, authorityClass: "SESSION_CONTROL_RIGHT", scopeType: "CHALLENGE", scopeId: CH }, true);
if (grant.body.kind !== "committed") throw new Error(`grant: ${JSON.stringify(grant)}`);
console.log(`WS=${WS} CH=${CH}`);
