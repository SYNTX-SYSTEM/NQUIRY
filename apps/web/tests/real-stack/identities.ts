/**
 * HD-3 DEV-ONLY identity provisioning, invoked out of band. Creates a
 * user + local credential ONLY (see scripts/dev_provision_local_identity.py).
 * Every membership, role and authority relation in the specs is then
 * established through the real product UI.
 */
import { execFileSync } from "node:child_process";
import path from "node:path";

export type DevIdentity = { readonly userId: string; readonly email: string; readonly password: string; readonly name: string };

const REPO_ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../../..");

export function provisionIdentity(label: string): DevIdentity {
  const stamp = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
  const email = `${label.toLowerCase()}-${stamp}@dev.local.test`;
  const password = `dev-${stamp}-password`;
  const name = `${label} ${stamp.slice(-4)}`;
  const python = process.env.REAL_STACK_PYTHON ?? "python3";
  const out = execFileSync(
    python,
    [path.join(REPO_ROOT, "scripts/dev_provision_local_identity.py"), "--email", email, "--name", name, "--password", password],
    {
      cwd: REPO_ROOT,
      env: {
        ...process.env,
        PYTHONPATH: path.join(REPO_ROOT, "packages"),
        NQUIRY_DEV_IDENTITY_PROVISIONING: "I_UNDERSTAND_THIS_IS_DEV_ONLY",
        DATABASE_URL:
          process.env.DATABASE_URL ?? "postgresql+psycopg://nquiry:nquiry_local_dev_only@localhost:15432/nquiry",
      },
    },
  ).toString();
  const parsed = JSON.parse(out.trim().split("\n").pop() ?? "{}") as { userId?: string };
  if (!parsed.userId) throw new Error(`identity provisioning returned no userId: ${out}`);
  return { userId: parsed.userId, email, password, name };
}
