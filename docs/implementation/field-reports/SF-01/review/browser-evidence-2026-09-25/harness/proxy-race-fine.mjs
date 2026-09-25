/** Finer-grained through-proxy falsifier for D-1: idle 4900..5000 ms in 10 ms steps, 64 sockets per burst. */
import http from "node:http";
const port = Number(process.env.PROXY_PORT ?? 13100);
const agent = new http.Agent({ keepAlive: false });
const N = 64;
const get = () => new Promise((resolve) => {
  const req = http.get({ host: "127.0.0.1", port, path: "/api/healthz", agent }, (res) => { res.resume(); res.on("end", () => resolve(res.statusCode)); });
  req.on("error", (e) => resolve(e.code));
});
const tally = {};
for (let idle = 4900; idle <= 5000; idle += 10) {
  await Promise.all(Array.from({ length: N }, get));
  await new Promise((r) => setTimeout(r, idle));
  for (const s of await Promise.all(Array.from({ length: N }, get))) tally[s] = (tally[s] ?? 0) + 1;
}
console.log(JSON.stringify({ port, answers: tally }));
