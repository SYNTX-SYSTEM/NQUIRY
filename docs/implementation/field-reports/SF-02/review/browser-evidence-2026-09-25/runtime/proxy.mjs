// SF-01 browser-inspection proxy (runtime-only, not part of the repository).
// One origin for the browser: pages -> Next.js (127.0.0.1:3000), /api/* -> FastAPI (127.0.0.1:8000, prefix stripped).
// Same-origin, so the API's CORS policy is never exercised and nothing in the application is changed.
import http from "node:http";
const PORT = Number(process.env.INSPECT_PORT ?? 13200);
// D-1 repair: never reuse an upstream connection. uvicorn closes idle keep-alive connections
// after 5 s and Node 22's default agent pools them, so a reused socket could be reset in flight
// (observed as 502 on GET /api/.../overview; reproduced by harness/proxy-keepalive-race.mjs).
const upstreamAgent = new http.Agent({ keepAlive: false });
http
  .createServer((req, res) => {
    const api = req.url.startsWith("/api/") || req.url === "/api";
    const target = api ? { port: 8000, path: req.url.slice(4) || "/" } : { port: 3000, path: req.url };
    const upstream = http.request(
      { host: "127.0.0.1", port: target.port, path: target.path, method: req.method, headers: req.headers, agent: upstreamAgent },
      (up) => {
        res.writeHead(up.statusCode ?? 502, up.headers);
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
