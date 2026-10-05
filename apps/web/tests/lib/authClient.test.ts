import { describe, expect, it, vi } from "vitest";
import {
  AUTH_CONTRACT_PRODUCER,
  AUTH_FORBIDDEN_KEYS,
  AUTH_METHOD_STATUSES,
  AUTH_METHOD_TYPES,
  AUTH_PROJECTIONS,
  LINK_PROJECTIONS,
  MalformedAuthResponse,
  PROOF_CLASSES,
  UnsafeNextTarget,
  availableProvider,
  fetchCurrentSession,
  fetchIdentityPresentation,
  googleLoginStart,
  isLocalNextTarget,
  linkStartAction,
  listMethods,
  listProviders,
  listSessions,
  login,
  loginStartUrl,
  logout,
  logoutAll,
  parseIdentityPresentation,
  parseLogoutAll,
  parseMethodList,
  parseProviderList,
  parseSessionList,
  parseSessionRevoke,
  parseUnlink,
  readAuthProjection,
  readLinkProjection,
  revokeSession,
  unlinkMethod,
  type ProviderSummary,
} from "../../lib/api/authClient";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

describe("login", () => {
  it("POSTs email/password to /auth/login with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    const result = await login("demo@nonproof.test", "secret-pw", fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/login"),
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email: "demo@nonproof.test", password: "secret-pw" }),
      }),
    );
    expect(result).toEqual({ kind: "ok", userId: "u-1" });
  });

  it("parses a denied response without throwing", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "INVALID_CREDENTIALS" }, 401));

    const result = await login("demo@nonproof.test", "wrong", fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "INVALID_CREDENTIALS" });
  });

  it("fails closed on an unrecognized response shape rather than defaulting to ok", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "surprising" }));

    await expect(login("demo@nonproof.test", "pw", fetchImpl)).rejects.toThrow(TypeError);
  });

  it("fails closed on a missing kind", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({}));

    await expect(login("demo@nonproof.test", "pw", fetchImpl)).rejects.toThrow(TypeError);
  });

  it("never sends the password as a URL query parameter", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    await login("demo@nonproof.test", "super-secret-value", fetchImpl);

    const calledUrl = fetchImpl.mock.calls[0][0] as string;
    expect(calledUrl).not.toContain("super-secret-value");
  });
});

describe("fetchCurrentSession", () => {
  it("issues a credentialed GET to /auth/me", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));

    const result = await fetchCurrentSession(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/me"),
      expect.objectContaining({ credentials: "include" }),
    );
    expect(result).toEqual({ kind: "ok", userId: "u-1" });
  });

  it("parses a denied (no session) response", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));

    const result = await fetchCurrentSession(fetchImpl);

    expect(result).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
});

describe("logout", () => {
  it("POSTs to /auth/logout with credentials included", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));

    await logout(fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining("/auth/logout"),
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });
});

// ===========================================================================
// AUTH/CYAN-01 — typed, fail-closed consumption of the live PURPLE AUTH contract
// (producer auth-identity @ aa32c4d; live assembly auth-aa32c4d-20261001T081014Z).
// Every fixture below is the serializer's own shape; every falsifier is one
// step outside it. UNKNOWN != OK. DENIED != OK. PROVIDER_OUTPUT != CYAN_INFERENCE.
// ===========================================================================

/** The exact live `GET /auth/providers` body of nquiry.condyn.eu (2026-10-03, read-only probe). */
const LIVE_PRODUCTION_PROVIDERS = {
  kind: "ok",
  providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" }],
} as const;

const UUID_A = "0f1e2d3c-4b5a-4968-8778-695a4b3c2d1e";
const UUID_B = "11111111-2222-4333-8444-555555555555";
const T0 = "2026-10-01T08:10:14+00:00";

function parsedGoogle(): ProviderSummary {
  return parseProviderList(LIVE_PRODUCTION_PROVIDERS).providers[0];
}

describe("AUTH/CYAN-01 contract identity", () => {
  it("names the reconstructed PURPLE producer, never a moving branch head as truth", () => {
    expect(AUTH_CONTRACT_PRODUCER).toEqual({
      field: "PURPLE_AUTH",
      branch: "auth-identity",
      commit: "e069fc19f5e39bfcc69dff358314d0527bd57f30",
      liveAssembly: "auth-e069fc1-20261004T140533Z",
    });
  });
  it("keeps every vocabulary closed and copied from the serializers", () => {
    expect([...PROOF_CLASSES]).toEqual(["PRODUCTION_PROVIDER", "TEST_PROVIDER"]);
    expect([...AUTH_METHOD_TYPES]).toEqual(["LOCAL_PASSWORD", "GOOGLE_OIDC", "TEST_PROVIDER"]);
    expect([...AUTH_METHOD_STATUSES]).toEqual(["ACTIVE", "REVOKED"]);
    expect([...AUTH_PROJECTIONS]).toEqual(["cancelled", "provider_unavailable", "provider_error", "failed", "unavailable"]);
    expect([...LINK_PROJECTIONS]).toEqual(["ok", "already_linked", "collision", "cancelled", "failed"]);
    // LOGIN != LINK: the two vocabularies share only the outcome words that both callbacks emit.
    expect(AUTH_PROJECTIONS).not.toContain("ok");
    expect(AUTH_PROJECTIONS).not.toContain("already_linked");
    expect(LINK_PROJECTIONS).not.toContain("provider_error");
    expect(AUTH_FORBIDDEN_KEYS).toContain("sessionToken");
    expect(AUTH_FORBIDDEN_KEYS).toContain("sub");
  });
});

describe("providers: the live production fixture", () => {
  it("parses the exact live shape and nothing beyond it", () => {
    const result = parseProviderList(LIVE_PRODUCTION_PROVIDERS);
    expect(result.kind).toBe("ok");
    expect(result.providers).toHaveLength(1);
    const [google] = result.providers;
    expect(google.providerId).toBe("google");
    expect(google.label).toBe("Google");
    expect(google.proofClass).toBe("PRODUCTION_PROVIDER");
    expect(Object.keys(google).sort()).toEqual(["label", "proofClass", "providerId"]);
  });
  it("derives Google availability ONLY from the parsed list", () => {
    const start = googleLoginStart(parseProviderList(LIVE_PRODUCTION_PROVIDERS), "/workspaces");
    expect(start.kind).toBe("available");
    if (start.kind !== "available") throw new Error("unreachable");
    expect(start.provider.providerId).toBe("google");
    expect(start.url).toBe("http://localhost:8000/auth/oidc/google/start?next=%2Fworkspaces");
  });
  it("an empty provider list means no Google: no hard-coded availability", () => {
    const empty = parseProviderList({ kind: "ok", providers: [] });
    expect(availableProvider(empty, "google")).toBeNull();
    expect(googleLoginStart(empty, "/")).toEqual({ kind: "unavailable" });
  });
  it("a list without google (only a test provider) means no Google; the test proof class is preserved, not upgraded", () => {
    const list = parseProviderList({ kind: "ok", providers: [{ providerId: "test", label: "Local test issuer", proofClass: "TEST_PROVIDER" }] });
    expect(googleLoginStart(list, "/")).toEqual({ kind: "unavailable" });
    expect(availableProvider(list, "test")?.proofClass).toBe("TEST_PROVIDER");
  });
  it("GETs /auth/providers with credentials and parses the live fixture", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(LIVE_PRODUCTION_PROVIDERS));
    const result = await listProviders(fetchImpl);
    expect(fetchImpl).toHaveBeenCalledWith(
      "http://localhost:8000/auth/providers",
      expect.objectContaining({ credentials: "include", headers: { Accept: "application/json" } }),
    );
    expect(result.providers[0].proofClass).toBe("PRODUCTION_PROVIDER");
  });
  it("a parsed provider carries no role, authority or permission (AUTHENTICATION != AUTHORIZATION)", () => {
    const google = parsedGoogle();
    for (const key of ["role", "authority", "permissions", "capabilities", "owner"]) {
      expect(key in google).toBe(false);
    }
  });
});

describe("providers: falsifiers (every unknown fails closed)", () => {
  const cases: ReadonlyArray<[string, unknown]> = [
    ["unknown proofClass", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PROVEN_PROVIDER" }] }],
    ["proofClass with different case", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "production_provider" }] }],
    ["missing proofClass", { kind: "ok", providers: [{ providerId: "google", label: "Google" }] }],
    ["extra field on a provider", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", available: true }] }],
    ["extra field on the envelope", { kind: "ok", providers: [], googleAvailable: true }],
    ["kind denied (the provider list has one shape)", { kind: "denied", reasonCode: "NO_SESSION" }],
    ["kind unknown", { kind: "providers", providers: [] }],
    ["missing kind", { providers: [] }],
    ["providers not an array", { kind: "ok", providers: { google: true } }],
    ["provider not an object", { kind: "ok", providers: ["google"] }],
    ["empty provider id", { kind: "ok", providers: [{ providerId: "", label: "Google", proofClass: "PRODUCTION_PROVIDER" }] }],
    ["non-string label", { kind: "ok", providers: [{ providerId: "google", label: null, proofClass: "PRODUCTION_PROVIDER" }] }],
    ["duplicate provider id", { kind: "ok", providers: [LIVE_PRODUCTION_PROVIDERS.providers[0], LIVE_PRODUCTION_PROVIDERS.providers[0]] }],
    ["forbidden key on the envelope", { kind: "ok", providers: [], sessionToken: "x" }],
    ["forbidden key on a provider", { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", clientSecret: "x" }] }],
    ["body is an array", [{ kind: "ok" }]],
    ["body is null", null],
    ["body is a string", "ok"],
  ];
  for (const [name, body] of cases) {
    it(`fails closed on ${name}`, () => {
      expect(() => parseProviderList(body)).toThrow(MalformedAuthResponse);
      expect(() => parseProviderList(body)).toThrow(TypeError);
    });
  }
  it("names the secret/subject law when a forbidden key is present (not merely an unexpected key)", () => {
    const envelope = { kind: "ok", providers: [], sessionToken: "x" };
    const nested = { kind: "ok", providers: [{ providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER", clientSecret: "x" }] };
    expect(() => parseProviderList(envelope)).toThrow(/forbidden key/);
    expect(() => parseProviderList(nested)).toThrow(/forbidden key/);
    expect(() => parseMethodList({ kind: "ok", methods: [{ methodId: UUID_A, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: null, provider: null, token: "t" }] })).toThrow(/forbidden key/);
    expect(() => parseUnlink({ kind: "ok", methodId: UUID_B, sessionsRevoked: 1, currentSessionEnded: false, sub: "x" })).toThrow(/forbidden key/);
  });
  it("fails closed on a non-JSON body instead of guessing", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(new Response("<html>503</html>", { status: 503, headers: { "Content-Type": "text/html" } }));
    await expect(listProviders(fetchImpl)).rejects.toThrow(MalformedAuthResponse);
  });
  it("a hand-built provider is not a parsed provider (type-level: availability only from the parsed response)", () => {
    const forged = { providerId: "google", label: "Google", proofClass: "PRODUCTION_PROVIDER" } as const;
    // @ts-expect-error -- the module-private brand is missing: a bare object is never a ProviderSummary.
    const build = () => loginStartUrl(forged, "/");
    expect(typeof build).toBe("function");
  });
});

describe("next target: PURPLE's local-destination rule, mirrored; unsafe is refused, never forwarded", () => {
  const safe = ["/", "/workspaces", "/workspaces/abc-1/sessions/s-2?tab=x#y", "/login?auth=failed", "/a~b", "/" + "x".repeat(1023)];
  const unsafe: ReadonlyArray<[string, unknown]> = [
    ["absolute https URL", "https://evil.example/"],
    ["absolute http URL", "http://evil.example"],
    ["scheme-relative URL", "//evil.example/"],
    ["backslash host trick", "/\\evil.example"],
    ["backslash later", "/a\\b"],
    ["javascript scheme", "javascript:alert(1)"],
    ["no leading slash", "workspaces"],
    ["empty", ""],
    ["space (header splitting)", "/a b"],
    ["newline (header splitting)", "/a\nb"],
    ["carriage return", "/a\rb"],
    ["tab", "/a\tb"],
    ["percent-encoded CRLF", "/a%0d%0aSet-Cookie:x"],
    ["percent-encoded NUL", "/a%00"],
    ["percent-encoded DEL", "/a%7F"],
    ["non-ASCII", "/ä"],
    ["too long", "/" + "x".repeat(1024)],
    ["not a string", 42],
    ["null", null],
    ["undefined", undefined],
    ["object", { toString: () => "/x" }],
  ];
  for (const target of safe) {
    it(`accepts the local destination ${JSON.stringify(target.slice(0, 40))}`, () => {
      expect(isLocalNextTarget(target)).toBe(true);
      expect(loginStartUrl(parsedGoogle(), target)).toContain("next=");
    });
  }
  for (const [name, target] of unsafe) {
    it(`refuses ${name}`, () => {
      expect(isLocalNextTarget(target)).toBe(false);
      expect(() => loginStartUrl(parsedGoogle(), target as string)).toThrow(UnsafeNextTarget);
      expect(() => linkStartAction(parsedGoogle(), target as string)).toThrow(UnsafeNextTarget);
      expect(() => googleLoginStart(parseProviderList(LIVE_PRODUCTION_PROVIDERS), target as string)).toThrow(UnsafeNextTarget);
    });
  }
  it("the refusal never echoes the candidate", () => {
    let message = "";
    try {
      loginStartUrl(parsedGoogle(), "https://evil.example/leak-me");
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).not.toContain("evil");
    expect(message).not.toContain("leak-me");
  });
});

describe("LOGIN start vs LINK start (LOGIN != LINK; LINK != ACCOUNT_CREATION)", () => {
  it("builds the login start as a GET navigation with an encoded next", () => {
    expect(loginStartUrl(parsedGoogle(), "/workspaces/w-1?x=1&y=2")).toBe(
      "http://localhost:8000/auth/oidc/google/start?next=%2Fworkspaces%2Fw-1%3Fx%3D1%26y%3D2",
    );
  });
  it("builds the link start as a POST form action on the link route, bound to an explicit local next", () => {
    const action = linkStartAction(parsedGoogle(), "/workspaces");
    expect(action).toEqual({ method: "POST", action: "http://localhost:8000/auth/oidc/google/link/start?next=%2Fworkspaces" });
    expect(action.action).not.toBe(loginStartUrl(parsedGoogle(), "/workspaces"));
    expect(action.action).toContain("/link/start");
    expect(loginStartUrl(parsedGoogle(), "/workspaces")).not.toContain("/link/");
  });
  it("encodes a provider id that is not URL-safe instead of trusting it", () => {
    const list = parseProviderList({ kind: "ok", providers: [{ providerId: "a/b?c", label: "Odd", proofClass: "TEST_PROVIDER" }] });
    expect(loginStartUrl(list.providers[0], "/")).toBe("http://localhost:8000/auth/oidc/a%2Fb%3Fc/start?next=%2F");
  });
});

describe("projections: vocabulary only, unknown is unknown (never failed, never ok)", () => {
  it("reads no projection from an empty query", () => {
    expect(readAuthProjection("")).toEqual({ kind: "none" });
    expect(readLinkProjection(new URLSearchParams(""))).toEqual({ kind: "none" });
    expect(readAuthProjection("?link=ok")).toEqual({ kind: "none" });
  });
  for (const word of AUTH_PROJECTIONS) {
    it(`reads the login projection ${word}`, () => {
      expect(readAuthProjection(`?auth=${word}`)).toEqual({ kind: "projection", projection: word });
    });
  }
  for (const word of LINK_PROJECTIONS) {
    it(`reads the link projection ${word}`, () => {
      expect(readLinkProjection(`?link=${word}&other=1`)).toEqual({ kind: "projection", projection: word });
    });
  }
  const unknownAuth = ["ok", "already_linked", "success", "FAILED", "failed ", "%3Cscript%3Ealert(1)%3C%2Fscript%3E", "", "provider_error%00"];
  for (const word of unknownAuth) {
    it(`treats auth=${JSON.stringify(word)} as unknown, not as failed`, () => {
      expect(readAuthProjection(`?auth=${word}`)).toEqual({ kind: "unknown" });
    });
  }
  const unknownLink = ["provider_error", "provider_unavailable", "unavailable", "linked", "OK", "ok%20", ""];
  for (const word of unknownLink) {
    it(`treats link=${JSON.stringify(word)} as unknown, not as ok`, () => {
      expect(readLinkProjection(`?link=${word}`)).toEqual({ kind: "unknown" });
    });
  }
  it("a repeated projection parameter is unknown (one callback, one word)", () => {
    expect(readAuthProjection("?auth=failed&auth=cancelled")).toEqual({ kind: "unknown" });
    expect(readLinkProjection("?link=ok&link=ok")).toEqual({ kind: "unknown" });
  });
});

describe("methods (GET /auth/methods)", () => {
  const METHODS_OK = {
    kind: "ok",
    methods: [
      { methodId: UUID_A, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: T0, provider: null },
      { methodId: UUID_B, methodType: "GOOGLE_OIDC", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: null, provider: { providerId: "google", email: "person@example.test" } },
    ],
  };
  it("parses the serializer shape", () => {
    const result = parseMethodList(METHODS_OK);
    expect(result).toEqual(METHODS_OK);
  });
  it("parses a provider method without an email", () => {
    const body = { kind: "ok", methods: [{ ...METHODS_OK.methods[1], provider: { providerId: "google", email: null } }] };
    expect(parseMethodList(body)).toEqual(body);
  });
  it("parses denied NO_SESSION without upgrading it", () => {
    expect(parseMethodList({ kind: "denied", reasonCode: "NO_SESSION" })).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
  it("GETs /auth/methods with credentials", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "NO_SESSION" }, 401));
    expect(await listMethods(fetchImpl)).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
    expect(fetchImpl).toHaveBeenCalledWith("http://localhost:8000/auth/methods", expect.objectContaining({ credentials: "include" }));
  });
  const m = METHODS_OK.methods[0];
  const falsifiers: ReadonlyArray<[string, unknown]> = [
    ["unknown methodType", { kind: "ok", methods: [{ ...m, methodType: "APPLE_OIDC" }] }],
    ["unknown status", { kind: "ok", methods: [{ ...m, status: "PENDING" }] }],
    ["extra key on a method", { kind: "ok", methods: [{ ...m, role: "Owner" }] }],
    ["missing provider key", { kind: "ok", methods: [{ methodId: UUID_A, methodType: "LOCAL_PASSWORD", status: "ACTIVE", createdAt: T0, lastAuthenticatedAt: null }] }],
    ["provider with an extra key", { kind: "ok", methods: [{ ...METHODS_OK.methods[1], provider: { providerId: "google", email: null, subject: "123" } }] }],
    ["provider missing providerId", { kind: "ok", methods: [{ ...METHODS_OK.methods[1], provider: { email: null } }] }],
    ["non-ISO createdAt", { kind: "ok", methods: [{ ...m, createdAt: "yesterday" }] }],
    ["non-UUID methodId", { kind: "ok", methods: [{ ...m, methodId: "method-1" }] }],
    ["lastAuthenticatedAt as number", { kind: "ok", methods: [{ ...m, lastAuthenticatedAt: 0 }] }],
    ["denied with an unknown reason", { kind: "denied", reasonCode: "SOMETHING_ELSE" }],
    ["denied without reasonCode", { kind: "denied" }],
    ["denied with extra key", { kind: "denied", reasonCode: "NO_SESSION", methods: [] }],
    ["kind rejected (the methods list never rejects)", { kind: "rejected", reasonCode: "X" }],
    ["kind unknown", { kind: "ok?", methods: [] }],
    ["methods not an array", { kind: "ok", methods: null }],
    ["forbidden nested key", { kind: "ok", methods: [{ ...m, token: "t" }] }],
  ];
  for (const [name, body] of falsifiers) {
    it(`fails closed on ${name}`, () => {
      expect(() => parseMethodList(body)).toThrow(MalformedAuthResponse);
    });
  }
});

describe("sessions (GET /auth/sessions, revoke, logout-all)", () => {
  const SESSIONS_OK = {
    kind: "ok",
    sessions: [
      { sessionId: UUID_A, issuedAt: T0, expiresAt: "2026-10-02T08:10:14+00:00", current: true, methodType: "LOCAL_PASSWORD" },
      { sessionId: UUID_B, issuedAt: T0, expiresAt: "2026-10-02T08:10:14+00:00", current: false, methodType: null },
    ],
  };
  it("parses the serializer shape, including a session no method produced", () => {
    expect(parseSessionList(SESSIONS_OK)).toEqual(SESSIONS_OK);
  });
  it("parses denied NO_SESSION", () => {
    expect(parseSessionList({ kind: "denied", reasonCode: "NO_SESSION" })).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
  const s = SESSIONS_OK.sessions[0];
  const listFalsifiers: ReadonlyArray<[string, unknown]> = [
    ["two current sessions", { kind: "ok", sessions: [s, { ...SESSIONS_OK.sessions[1], current: true }] }],
    ["unknown methodType", { kind: "ok", sessions: [{ ...s, methodType: "MAGIC_LINK" }] }],
    ["current as string", { kind: "ok", sessions: [{ ...s, current: "true" }] }],
    ["missing expiresAt", { kind: "ok", sessions: [{ sessionId: UUID_A, issuedAt: T0, current: true, methodType: null }] }],
    ["extra key", { kind: "ok", sessions: [{ ...s, ipAddress: "127.0.0.1" }] }],
    ["forbidden key tokenHash", { kind: "ok", sessions: [{ ...s, tokenHash: "abc" }] }],
    ["denied unknown reason", { kind: "denied", reasonCode: "SESSION_NOT_FOUND" }],
    ["kind unknown", { kind: "partial", sessions: [] }],
  ];
  for (const [name, body] of listFalsifiers) {
    it(`list fails closed on ${name}`, () => {
      expect(() => parseSessionList(body)).toThrow(MalformedAuthResponse);
    });
  }
  it("revoke: parses ok, denied and rejected exactly", () => {
    expect(parseSessionRevoke({ kind: "ok" })).toEqual({ kind: "ok" });
    expect(parseSessionRevoke({ kind: "denied", reasonCode: "SESSION_NOT_FOUND" })).toEqual({ kind: "denied", reasonCode: "SESSION_NOT_FOUND" });
    expect(parseSessionRevoke({ kind: "denied", reasonCode: "NO_SESSION" })).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
    expect(parseSessionRevoke({ kind: "rejected", reasonCode: "MALFORMED_SESSION_ID" })).toEqual({ kind: "rejected", reasonCode: "MALFORMED_SESSION_ID" });
  });
  const revokeFalsifiers: ReadonlyArray<[string, unknown]> = [
    ["ok with an extra key", { kind: "ok", revoked: true }],
    ["denied with a rejected reason", { kind: "denied", reasonCode: "MALFORMED_SESSION_ID" }],
    ["rejected with a denied reason", { kind: "rejected", reasonCode: "NO_SESSION" }],
    ["unknown reason", { kind: "denied", reasonCode: "FORBIDDEN" }],
    ["unknown kind", { kind: "revoked" }],
  ];
  for (const [name, body] of revokeFalsifiers) {
    it(`revoke fails closed on ${name}`, () => {
      expect(() => parseSessionRevoke(body)).toThrow(MalformedAuthResponse);
    });
  }
  it("logout-all: parses the revoked count and denied", () => {
    expect(parseLogoutAll({ kind: "ok", revokedSessions: 3 })).toEqual({ kind: "ok", revokedSessions: 3 });
    expect(parseLogoutAll({ kind: "ok", revokedSessions: 0 })).toEqual({ kind: "ok", revokedSessions: 0 });
    expect(parseLogoutAll({ kind: "denied", reasonCode: "NO_SESSION" })).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
  const logoutFalsifiers: ReadonlyArray<[string, unknown]> = [
    ["negative count", { kind: "ok", revokedSessions: -1 }],
    ["fractional count", { kind: "ok", revokedSessions: 1.5 }],
    ["string count", { kind: "ok", revokedSessions: "3" }],
    ["missing count", { kind: "ok" }],
    ["unknown reason", { kind: "denied", reasonCode: "SESSION_NOT_FOUND" }],
    ["unknown kind", { kind: "rejected", reasonCode: "X" }],
  ];
  for (const [name, body] of logoutFalsifiers) {
    it(`logout-all fails closed on ${name}`, () => {
      expect(() => parseLogoutAll(body)).toThrow(MalformedAuthResponse);
    });
  }
  it("fetches the three contacts with the right method, path and credentials", async () => {
    const list = vi.fn().mockResolvedValue(jsonResponse(SESSIONS_OK));
    await listSessions(list);
    expect(list).toHaveBeenCalledWith("http://localhost:8000/auth/sessions", expect.objectContaining({ credentials: "include" }));
    expect((list.mock.calls[0][1] as RequestInit).method).toBeUndefined();

    const revoke = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok" }));
    await revokeSession("a/b c", revoke);
    expect(revoke).toHaveBeenCalledWith(
      "http://localhost:8000/auth/sessions/a%2Fb%20c/revoke",
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );

    const all = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", revokedSessions: 2 }));
    expect(await logoutAll(all)).toEqual({ kind: "ok", revokedSessions: 2 });
    expect(all).toHaveBeenCalledWith("http://localhost:8000/auth/logout-all", expect.objectContaining({ method: "POST", credentials: "include" }));
  });
});

describe("unlink (POST /auth/methods/{methodId}/unlink)", () => {
  const UNLINK_OK = { kind: "ok", methodId: UUID_B, sessionsRevoked: 1, currentSessionEnded: false };
  it("parses ok, every denied reason and the rejected reason exactly", () => {
    expect(parseUnlink(UNLINK_OK)).toEqual(UNLINK_OK);
    for (const reasonCode of ["NO_SESSION", "UNLINK_DENIED", "LAST_METHOD"]) {
      expect(parseUnlink({ kind: "denied", reasonCode })).toEqual({ kind: "denied", reasonCode });
    }
    expect(parseUnlink({ kind: "rejected", reasonCode: "MALFORMED_METHOD_ID" })).toEqual({ kind: "rejected", reasonCode: "MALFORMED_METHOD_ID" });
  });
  const falsifiers: ReadonlyArray<[string, unknown]> = [
    ["sessionsRevoked as string", { ...UNLINK_OK, sessionsRevoked: "1" }],
    ["currentSessionEnded missing", { kind: "ok", methodId: UUID_B, sessionsRevoked: 1 }],
    ["extra key", { ...UNLINK_OK, unlinked: true }],
    ["non-UUID methodId", { ...UNLINK_OK, methodId: "m-1" }],
    ["unknown denied reason", { kind: "denied", reasonCode: "SESSION_NOT_FOUND" }],
    ["unknown kind unavailable", { kind: "unavailable", reasonCode: "PROVIDER_NOT_CONFIGURED" }],
    ["forbidden key", { ...UNLINK_OK, sub: "x" }],
  ];
  for (const [name, body] of falsifiers) {
    it(`fails closed on ${name}`, () => {
      expect(() => parseUnlink(body)).toThrow(MalformedAuthResponse);
    });
  }
  it("POSTs to the encoded unlink path with credentials", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ kind: "denied", reasonCode: "LAST_METHOD" }, 409));
    expect(await unlinkMethod(UUID_B, fetchImpl)).toEqual({ kind: "denied", reasonCode: "LAST_METHOD" });
    expect(fetchImpl).toHaveBeenCalledWith(
      `http://localhost:8000/auth/methods/${UUID_B}/unlink`,
      expect.objectContaining({ method: "POST", credentials: "include" }),
    );
  });
});

describe("preservation: the F02 contacts are untouched by AUTH/CYAN-01", () => {
  it("login still parses its own three-case shape and still fails closed", async () => {
    const ok = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1" }));
    expect(await login("a@b.test", "pw", ok)).toEqual({ kind: "ok", userId: "u-1" });
    const unknown = vi.fn().mockResolvedValue(jsonResponse({ kind: "ok", userId: "u-1", role: "Owner" }));
    // The F02 parser reads its fields and ignores the rest; it never surfaces a role.
    expect(await login("a@b.test", "pw", unknown)).toEqual({ kind: "ok", userId: "u-1" });
  });
});

// ===========================================================================
// CYAN_IDENTITY_PRESENTATION_CONSUMPTION_01 — GET /auth/identity (PURPLE_IDENTITY_PRESENTATION_01 @ 2ec05c0)
// ===========================================================================
describe("identity presentation (GET /auth/identity)", () => {
  /** Live-shaped fixture (values evidence-derived from the production proof, never product code). */
  const LIVE_IDENTITY = { kind: "ok", userId: "7dd6e767-1111-4111-8111-111111111111", displayName: "tobi", canonicalEmail: "tobias@thescaleforge.com" };
  it("accepts the exact production shape and nothing beyond it", () => {
    expect(parseIdentityPresentation(LIVE_IDENTITY)).toEqual(LIVE_IDENTITY);
    expect(Object.keys(parseIdentityPresentation(LIVE_IDENTITY)).sort()).toEqual(["canonicalEmail", "displayName", "kind", "userId"]);
  });
  it("parses denied NO_SESSION (the one class for no session and no identity row)", () => {
    expect(parseIdentityPresentation({ kind: "denied", reasonCode: "NO_SESSION" })).toEqual({ kind: "denied", reasonCode: "NO_SESSION" });
  });
  const falsifiers: ReadonlyArray<[string, unknown]> = [
    ["missing displayName", { kind: "ok", userId: LIVE_IDENTITY.userId, canonicalEmail: "a@b.test" }],
    ["missing canonicalEmail", { kind: "ok", userId: LIVE_IDENTITY.userId, displayName: "x" }],
    ["empty displayName (nothing is defaulted)", { ...LIVE_IDENTITY, displayName: "" }],
    ["blank canonicalEmail", { ...LIVE_IDENTITY, canonicalEmail: "   " }],
    ["null displayName", { ...LIVE_IDENTITY, displayName: null }],
    ["extra field (providerEmail)", { ...LIVE_IDENTITY, providerEmail: "x@y.test" }],
    ["extra field (role)", { ...LIVE_IDENTITY, role: "Owner" }],
    ["non-UUID userId", { ...LIVE_IDENTITY, userId: "u-1" }],
    ["unknown reason", { kind: "denied", reasonCode: "IDENTITY_NOT_FOUND" }],
    ["unknown kind", { kind: "unavailable", reasonCode: "X" }],
    ["forbidden key", { ...LIVE_IDENTITY, sub: "google-subject" }],
    ["null body", null],
  ];
  for (const [name, body] of falsifiers) {
    it(`fails closed on ${name}`, () => {
      expect(() => parseIdentityPresentation(body)).toThrow(MalformedAuthResponse);
    });
  }
  it("GETs /auth/identity with credentials; the API mount is never prefixed", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(LIVE_IDENTITY));
    expect(await fetchIdentityPresentation(fetchImpl)).toEqual(LIVE_IDENTITY);
    expect(fetchImpl).toHaveBeenCalledWith("http://localhost:8000/auth/identity", expect.objectContaining({ credentials: "include", headers: { Accept: "application/json" } }));
  });
  it("a non-JSON body fails closed", async () => {
    await expect(fetchIdentityPresentation(vi.fn().mockResolvedValue(new Response("<html>", { status: 502 })))).rejects.toThrow(MalformedAuthResponse);
  });
});
