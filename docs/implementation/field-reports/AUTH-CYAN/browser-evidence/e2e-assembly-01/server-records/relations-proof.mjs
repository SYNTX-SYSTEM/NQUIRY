// CYAN_REAL_E2E_ASSEMBLY_01 relations + mutation proof over the APPLIED vhost text and the review compose text.
// The relations are asserted as text predicates; mutations are semantic corruptions applied to copies of the text.
import { readFileSync } from "node:fs";
const vhostBefore = readFileSync(new URL("./vhost.before", import.meta.url), "utf8");
const vhost = readFileSync(new URL("./vhost.candidate", import.meta.url), "utf8");
const compose = readFileSync(new URL("./compose.applied.yaml", import.meta.url), "utf8").split("\n").filter((l) => !/^\s*#/.test(l)).join("\n");
const body = (text, header) => { const tls = text.indexOf("listen 443"); const i = text.indexOf(header, tls < 0 ? 0 : tls); if (i < 0) return null; const open = text.indexOf("{", i); let d = 0; for (let j = open; j < text.length; j++) { if (text[j] === "{") d++; else if (text[j] === "}") { d--; if (d === 0) return text.slice(open, j + 1); } } return null; };
function relations(v, c) {
  const live = body(v, "location / {"); const api = body(v, "location /api/ {"); const rev = body(v, "location ^~ /cy-review/ {"); const revExact = body(v, "location = /cy-review {");
  const checks = {
    "live root → 3400": !!live && /proxy_pass http:\/\/127\.0\.0\.1:3400;/.test(live),
    "api → 8400 with the rewrite and the binding-cookie path": !!api && /proxy_pass http:\/\/127\.0\.0\.1:8400;/.test(api) && /rewrite \^\/api\/\(\.\*\)\$ \/\$1 break;/.test(api) && /proxy_cookie_path \/auth \/api\/auth;/.test(api),
    "review mount → 3402 (both locations)": !!rev && !!revExact && /proxy_pass http:\/\/127\.0\.0\.1:3402;/.test(rev) && /proxy_pass http:\/\/127\.0\.0\.1:3402;/.test(revExact),
    "review locations carry no rewrite, no cookie rewrite, no /api": !!rev && !/rewrite|proxy_cookie|\/api/.test(rev) && !/rewrite|proxy_cookie|\/api/.test(revExact),
    "no location nests /api beneath /cy-review": !/location[^{]*\/cy-review\/api/.test(v),
    "live root and api blocks byte-equal to before": body(vhostBefore, "location / {") === live && body(vhostBefore, "location /api/ {") === api && live !== null && api !== null,
    "server_name unchanged; no new server/hostname": (v.match(/server_name [^;]+;/g) ?? []).join() === (vhostBefore.match(/server_name [^;]+;/g) ?? []).join() && (v.match(/\bserver\s*\{/g) ?? []).length === (vhostBefore.match(/\bserver\s*\{/g) ?? []).length,
    "callback path untouched (no cy-review callback)": !/cy-review\/api\/auth\/oidc|oidc\/google\/callback/.test(v),
    "delta = exactly the two review locations": v.replace(body(v, "location = /cy-review {") ?? "", "").replace(body(v, "location ^~ /cy-review/ {") ?? "", "").replace(/ *# CYAN_REAL_E2E_ASSEMBLY_01[\s\S]*?\n(?= *location = \/cy-review)/, "").replace(/ *location = \/cy-review \s*\n/, "").replace(/ *location \^~ \/cy-review\/ \s*\n+/, "").replace(/\n{3,}/g, "\n\n") === vhostBefore.replace(/\n{3,}/g, "\n\n"),
    "compose: web only": (c.match(/^  [a-z]+:\s*$/gm) ?? []).join() === "  web:",
    "compose: api base is the production /api, mount /cy-review, no mount in the api base": /NEXT_PUBLIC_API_BASE_URL: https:\/\/nquiry\.condyn\.eu\/api$/m.test(c) && /NEXT_PUBLIC_FRONTEND_MOUNT: \/cy-review$/m.test(c) && !/cy-review\/api/.test(c),
    "compose: loopback 3402 only, no other port": (c.match(/^\s+- '([^']+)'/gm) ?? []).join() === "      - '127.0.0.1:3402:3000'",
    "compose: no secrets, no env_file, no DATABASE_URL, no provider/google/cookie keys": !/env_file|DATABASE_URL|POSTGRES|NQUIRY_GOOGLE|NQUIRY_AUTH_PROVIDER_MODE|COOKIE|SECRET|CLIENT_ID/i.test(c),
    "compose: no postgres/api/worker image or depends_on": !/postgres|api\.Dockerfile|worker|depends_on/.test(c),
  };
  return checks;
}
const base = relations(vhost, compose);
const failedBase = Object.entries(base).filter(([, ok]) => !ok);
console.log(`relations: ${Object.keys(base).length - failedBase.length}/${Object.keys(base).length} hold${failedBase.length ? " — FAILED: " + failedBase.map(([k]) => k).join("; ") : ""}`);
const MUT = [
  ["M1 review location routes to the live web", (v) => v.replace(/(location \^~ \/cy-review\/ \{[\s\S]*?proxy_pass http:\/\/127\.0\.0\.1:)3402/, "$13400"), compose],
  ["M2 review location rewrites /api through the candidate", (v) => v.replace("location ^~ /cy-review/ {", "location ^~ /cy-review/ {\n        rewrite ^/cy-review/api/(.*)$ /api/$1 break;"), compose],
  ["M3 candidate API base becomes /cy-review/api", vhost, (c) => c.replace(/https:\/\/nquiry\.condyn\.eu\/api/g, "https://nquiry.condyn.eu/cy-review/api")],
  ["M4 candidate starts its own API", vhost, (c) => c + "\n  api:\n    build:\n      dockerfile: api.Dockerfile\n"],
  ["M5 candidate starts its own DB", vhost, (c) => c + "\n  postgres:\n    image: postgres:17\n"],
  ["M6 live root routes to the candidate", (v) => v.replace(/(location \/ \{[\s\S]*?proxy_pass http:\/\/127\.0\.0\.1:)3400/, "$13402"), compose],
  ["M7 Google callback rewritten beneath /cy-review", (v) => v.replace("location ^~ /cy-review/ {", "location = /cy-review/api/auth/oidc/google/callback {\n        proxy_pass http://127.0.0.1:8400;\n    }\n    location ^~ /cy-review/ {"), compose],
  ["M8 candidate requires a separate cookie scope", (v) => v.replace("location ^~ /cy-review/ {", "location ^~ /cy-review/ {\n        proxy_cookie_path / /cy-review/;"), compose],
  ["M9 candidate receives an unnecessary provider/auth secret", vhost, (c) => c.replace("NEXT_TELEMETRY_DISABLED: '1'", "NEXT_TELEMETRY_DISABLED: '1'\n      NQUIRY_GOOGLE_CLIENT_SECRET: x")],
  ["M10 rollback removes or alters the live root", (v) => v.replace(/(location \/ \{[\s\S]*?)proxy_set_header Host \$host;\n/, "$1"), compose],
  ["M11 rollback removes or alters /api", (v) => v.replace("        proxy_cookie_path /auth /api/auth;\n", ""), compose],
  ["M12 candidate exposed on another host / port", vhost, (c) => c.replace("'127.0.0.1:3402:3000'", "'0.0.0.0:3402:3000'")],
];
let killed = 0;
for (const [name, v, c] of MUT) {
  const r = relations(typeof v === "function" ? v(vhost) : v, typeof c === "function" ? c(compose) : c);
  const dead = Object.values(r).some((ok) => !ok);
  if (dead) killed++;
  console.log(`${name}: ${dead ? "KILLED" : "SURVIVED"}`);
}
console.log(`${killed}/${MUT.length} mutations killed`);
process.exit(failedBase.length === 0 && killed === MUT.length ? 0 : 1);
