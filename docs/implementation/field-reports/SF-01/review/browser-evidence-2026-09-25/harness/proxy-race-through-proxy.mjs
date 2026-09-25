/**
 * Integration proof for D-1: the burst / idle-at-5s / burst pattern THROUGH the inspection proxy
 * (fresh client connections, so only the proxy->upstream path can race). Before the repair the
 * proxy answered 502 when its pooled upstream socket was reset; after it, every answer must be 200.
 *   node proxy-race-through-proxy.mjs   (host; runtime at http://127.0.0.1:13100)
 */
import http from "node:http";
const agent = new http.Agent({ keepAlive: false });
const N = 48;
const get = () =>
  new Promise((resolve) => {
    const req = http.get({ host: "127.0.0.1", port: Number(process.env.PROXY_PORT ?? 13100), path: "/api/healthz", agent }, (res) => {
      res.resume();
      res.on("end", () => resolve(res.statusCode));
    });
    req.on("error", (e) => resolve(e.code));
  });
const tally = {};
for (const idle of [4990, 5000, 5010, 5020, 5000, 5000]) {
  await Promise.all(Array.from({ length: N }, get));
  await new Promise((r) => setTimeout(r, idle));
  for (const s of await Promise.all(Array.from({ length: N }, get))) tally[s] = (tally[s] ?? 0) + 1;
}
console.log(JSON.stringify({ throughProxyPort: Number(process.env.PROXY_PORT ?? 13100), answers: tally }));
