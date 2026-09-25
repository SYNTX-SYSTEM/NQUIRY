/** SF-02 WU-SF02.1: human position is a sourced label (22 §29.1 viewer/participant projection), never a gate. */
import { describe, expect, it } from "vitest";
import { humanPosition } from "../../lib/field/humanPosition";

describe("humanPosition", () => {
  it("describes the projected relations in semantic order", () => {
    const p = humanPosition(
      { userId: "u1", role: "Facilitator", isSessionController: true, isGovernanceRoot: false },
      { scope: "session", participantIds: ["u1", "u2"] },
    );
    expect(p.relations).toEqual(["Role: Facilitator", "Session controller", "Participant"]);
    expect(p.sentence).toBe("You: Role: Facilitator · Session controller · Participant");
  });
  it("names the absence of a relation explicitly (absence is not missing data)", () => {
    const p = humanPosition({ userId: "u9", role: null, isSessionController: false }, { scope: "session", participantIds: ["u1"] });
    expect(p.relations).toEqual(["No role in this Workspace", "Not the Session controller", "Not a participant"]);
  });
  it("workspace scope has no session relations", () => {
    expect(humanPosition({ userId: "u", role: "Owner", governanceCapable: true }, { scope: "workspace" }).relations).toEqual([
      "Role: Owner",
      "Workspace governance root",
    ]);
  });
});
