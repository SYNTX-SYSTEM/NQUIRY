/**
 * SF-03 relational reciprocity (doc 23 §8, §15.3): PRESENTATION-ONLY mapping between what the human focuses or
 * hovers and the instrument / relation family that belongs to it. It sets no state, implies no authority and
 * touches no capability; it only names which region responds. Keyboard focus and pointer hover use the same map.
 */
export type RelationFamily = "action" | "governance" | "proof" | "context";

export type OrbitKind = "containment" | "participation" | "governance" | "evidence" | "lifecycle" | "capability";
export type PlaneKind = "action" | "governance" | "proof" | "human" | "frozen" | "boundary" | "context";

/** An orbit's nodes relate to the instrument that acts on / explains them. */
export function relationOfOrbit(kind: OrbitKind): RelationFamily {
  switch (kind) {
    case "containment":
    case "capability":
    case "lifecycle":
      return "action";
    case "participation":
    case "governance":
      return "governance";
    case "evidence":
      return "proof";
  }
}

/** An instrument relates back to the relation family it serves. */
export function relationOfPlane(kind: PlaneKind): RelationFamily {
  switch (kind) {
    case "action":
    case "human":
    case "frozen":
    case "boundary":
      return "action";
    case "governance":
      return "governance";
    case "proof":
      return "proof";
    case "context":
      return "context";
  }
}
