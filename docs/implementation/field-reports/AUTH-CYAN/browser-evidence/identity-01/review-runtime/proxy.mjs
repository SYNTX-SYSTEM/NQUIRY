// SF-01 browser-inspection proxy (runtime-only, not part of the repository).
// One origin for the browser: pages -> Next.js (127.0.0.1:3000), /api/* -> FastAPI (127.0.0.1:8000, prefix stripped).
// Same-origin, so the API's CORS policy is never exercised and nothing in the application is changed.
import http from "node:http";
import { methodsBody, reviewState, sessionsBody, transitionCookie } from "./review-auth-fixture.mjs";
const PORT = Number(process.env.INSPECT_PORT ?? 13200);
// D-1 repair: never reuse an upstream connection (uvicorn closes idle keep-alive connections after 5 s).
const upstreamAgent = new http.Agent({ keepAlive: false });

// AUTH/CYAN-02: the pinned RED producer has no PURPLE AUTH routes. GET /api/auth/providers answers with the exact live
// production body of nquiry.condyn.eu (read-only probe 2026-10-03); the login start route is a labelled review boundary.
const PROVIDERS_FIXTURE = JSON.stringify({ kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] });
const FIXTURE = (what) => ({ "content-type": "application/json", "x-nquiry-review-fixture": `FIXTURE_NON_PROOF ${what}` });
const page = (title, body) =>
  `<!doctype html><meta name="viewport" content="width=device-width"><body style="margin:0;min-height:100vh;display:grid;place-items:center;background:#050a15;color:#dfe7ff;font:16px/1.5 system-ui"><main style="max-width:36rem;padding:24px"><p style="letter-spacing:.14em;text-transform:uppercase;font-size:.75rem;opacity:.7">Review boundary</p><h1 style="font-size:1.4rem">${title}</h1>${body}</main>`;

function reviewFixture(req, res) {
  const url = req.url.split("?")[0];
  const state = reviewState(req.headers.cookie);
  if (req.method === "GET" && url === "/api/auth/providers") {
    res.writeHead(200, FIXTURE("live-shape copy 2026-10-03"));
    res.end(PROVIDERS_FIXTURE);
    return true;
  }
  // AUTH/CYAN-IDENTITY-01 (field repair): sessions follow the recorded transition; methods are the linked pair.
  if (req.method === "GET" && url === "/api/auth/sessions") {
    res.writeHead(200, FIXTURE(`live-shape sessions · transition=${state ?? "none (methodType null)"}`));
    res.end(JSON.stringify(sessionsBody(state)));
    return true;
  }
  if (req.method === "GET" && url === "/api/auth/methods") {
    res.writeHead(200, FIXTURE("live-shape methods (linked pair; never the current-method source)"));
    res.end(JSON.stringify(methodsBody()));
    return true;
  }
  if (req.method === "GET" && url === "/api/auth/oidc/google/start") {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8", "x-nquiry-review-fixture": "FIXTURE_NON_PROOF review boundary" });
    res.end(page("The provider start is not available in this review runtime.",
      `<p>The Access Field navigated here by GET to the typed LOGIN start route. This runtime serves the pinned RED producer, which has no PURPLE AUTH routes and no Google client: no login is proven here (GOOGLE_AVAILABLE != GOOGLE_LOGIN_PROVEN). The live route exists on nquiry.condyn.eu and is not exercised by this review.</p>
       <p><a href="/login" style="color:#8fe3ff">Back to the Access Field</a></p>
       <hr style="border:0;border-top:1px solid #34486b;margin:24px 0">
       <p style="letter-spacing:.14em;text-transform:uppercase;font-size:.75rem;opacity:.7">Review transition (FIXTURE_NON_PROOF)</p>
       <p>For the review of the identity projection only: record that the CURRENT session of this (already locally authenticated) review identity was produced by GOOGLE_OIDC. No Google is contacted; nothing is proven. A local login or a logout clears it.</p>
       <form method="post" action="/api/review/google-transition"><button type="submit" style="font:inherit;padding:8px 16px;border-radius:999px;border:1px solid #58dcff;background:transparent;color:#58dcff">Enter the Google review state</button></form>`));
    return true;
  }
  if (req.method === "POST" && url === "/api/review/google-transition") {
    res.writeHead(303, { location: "/workspaces", "set-cookie": transitionCookie("google"), "x-nquiry-review-fixture": "FIXTURE_NON_PROOF google review transition" });
    res.end();
    return true;
  }
  return false;
}

http
  .createServer((req, res) => {
    if (reviewFixture(req, res)) return;
    const url = req.url.split("?")[0];
    const api = req.url.startsWith("/api/") || req.url === "/api";
    const target = api ? { port: 8000, path: req.url.slice(4) || "/" } : { port: 3000, path: req.url };
    const upstream = http.request(
      { host: "127.0.0.1", port: target.port, path: target.path, method: req.method, headers: req.headers, agent: upstreamAgent },
      (up) => {
        const headers = { ...up.headers };
        // the transition that produced the state: a successful local login records "local"; a logout clears it
        const cookies = [].concat(headers["set-cookie"] ?? []);
        if (req.method === "POST" && url === "/api/auth/login" && up.statusCode === 200) cookies.push(transitionCookie("local"));
        if (req.method === "POST" && url === "/api/auth/logout") cookies.push(transitionCookie(null));
        if (cookies.length) headers["set-cookie"] = cookies;
        res.writeHead(up.statusCode ?? 502, headers);
        up.pipe(res);
      },
    );
    upstream.on("error", (err) => {
      res.writeHead(502, { "content-type": "text/plain" });
      res.end(`inspect proxy: upstream ${target.port} unavailable (${err.code})`);
    });
    req.pipe(upstream);
  })
  .listen(PORT, "0.0.0.0", () => console.log(`inspect proxy on :${PORT}`));
