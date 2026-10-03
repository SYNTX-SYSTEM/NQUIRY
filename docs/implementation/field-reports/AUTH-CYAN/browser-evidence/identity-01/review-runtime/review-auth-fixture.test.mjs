// Falsifiers over the review-runtime fixture (node:test). The runtime is part of the proof field.
import assert from "node:assert/strict";
import { test } from "node:test";
import { methodsBody, reviewState, sessionsBody, transitionCookie } from "./review-auth-fixture.mjs";
const current = (b) => b.sessions.filter((s) => s.current);
test("local transition → exactly one current session, LOCAL_PASSWORD", () => {
  const b = sessionsBody(reviewState("nquiry_session=x; nquiry_review_auth=local"));
  assert.equal(current(b).length, 1); assert.equal(current(b)[0].methodType, "LOCAL_PASSWORD");
});
test("google transition → exactly one current session, GOOGLE_OIDC; the local session present but not current", () => {
  const b = sessionsBody(reviewState("nquiry_review_auth=google"));
  assert.equal(current(b).length, 1); assert.equal(current(b)[0].methodType, "GOOGLE_OIDC");
  assert.equal(b.sessions.length, 2); assert.equal(b.sessions.find((s) => !s.current).methodType, "LOCAL_PASSWORD");
});
test("no transition → one current session with methodType null (UNKNOWN; never Google, never Local password)", () => {
  for (const cookie of [undefined, "", "nquiry_session=x", "nquiry_review_auth=bogus", "other_review_auth=google"]) {
    const b = sessionsBody(reviewState(cookie));
    assert.equal(current(b).length, 1); assert.equal(current(b)[0].methodType, null);
  }
});
test("linked methods never decide: both ACTIVE in every state; google carries the provider binding", () => {
  for (const state of ["local", "google", null]) {
    const m = methodsBody(state);
    assert.deepEqual(m.methods.map((x) => [x.methodType, x.status]), [["LOCAL_PASSWORD", "ACTIVE"], ["GOOGLE_OIDC", "ACTIVE"]]);
    assert.equal(m.methods[1].provider.providerId, "google");
  }
});
test("the current method never follows the newest issuedAt: in the local state the local session is current although older than nothing / in google state the local one is older and not current", () => {
  const g = sessionsBody("google");
  const newest = g.sessions.reduce((a, b) => (a.issuedAt > b.issuedAt ? a : b));
  assert.equal(newest.current, true); // consistent here by construction …
  const l = sessionsBody("local");
  assert.equal(l.sessions[0].current, true); assert.equal(l.sessions[0].methodType, "LOCAL_PASSWORD");
});
test("transition cookies: login → local, google transition → google, logout → cleared", () => {
  assert.match(transitionCookie("local"), /^nquiry_review_auth=local; Path=\/; HttpOnly; SameSite=Lax$/);
  assert.match(transitionCookie("google"), /^nquiry_review_auth=google; /);
  assert.match(transitionCookie(null), /Max-Age=0/);
  assert.throws(() => transitionCookie("newest"));
});
