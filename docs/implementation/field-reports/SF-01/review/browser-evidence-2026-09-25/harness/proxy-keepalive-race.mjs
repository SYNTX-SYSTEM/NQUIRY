/**
 * Falsifier for OPEN->REPAIRED defect D-1 (inspection proxy 502): does reusing a pooled
 * upstream connection right at uvicorn's 5 s keep-alive timeout produce socket errors?
 * Runs inside the inspection runner container (same Node as the proxy):
 *   docker exec nquiry-sf01-inspect-runner node /evidence/proxy-keepalive-race.mjs <keepalive|fresh>
 * Opens N pooled connections, idles for exactly the server's keep-alive timeout, reuses them.
 */
import http from "node:http";
const mode = process.argv[2] ?? "keepalive";
const agent = mode === "keepalive" ? new http.Agent({ keepAlive: true, maxSockets: 64 }) : new http.Agent({ keepAlive: false });
const N = 48;
const get = () =>
  new Promise((resolve) => {
    const req = http.get({ host: "127.0.0.1", port: 8000, path: "/healthz", agent }, (res) => {
      res.resume();
      res.on("end", () => resolve(res.statusCode));
    });
    req.on("error", (e) => resolve(e.code));
  });
let errors = 0, total = 0;
for (const idle of [4990, 5000, 5010, 5020]) {
  await Promise.all(Array.from({ length: N }, get));
  await new Promise((r) => setTimeout(r, idle));
  const out = await Promise.all(Array.from({ length: N }, get));
  total += out.length;
  errors += out.filter((s) => s !== 200).length;
}
console.log(JSON.stringify({ mode, total, errors }));
process.exit(0);
