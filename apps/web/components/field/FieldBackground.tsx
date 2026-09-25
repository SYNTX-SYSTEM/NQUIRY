/**
 * SF-02/SF-03 Background Presentation Field (22 §17; doc 23 §5): depth, presence and continuity across the WHOLE
 * viewport — behind the rail, the topology and the instruments.
 *
 * Presentation only. It makes no authoritative claim: `regime` is the surface CLASS (22 §17.3), never backend state.
 * Layers (all `aria-hidden`, all cheap): a static depth gradient; a static constellation texture; three bounded
 * nebular blobs that drift extremely slowly on their own compositor layers (transform only, ±3 % of the viewport
 * over minutes); a bounded breathing luminosity (opacity only); static orbital traces; a handful of rare particles
 * whose opacity fades over ~1–2 minutes. Reduced motion removes every animation through the global rule and keeps
 * every layer, so depth survives without motion (doc 23 §5.4). No DOM particle field, no canvas, no timers, no
 * filters over large areas (22 §35). Nothing here carries meaning (doc 23 §5.3).
 */
export type BackgroundRegime =
  | "access"
  | "workspace-access"
  | "workspace"
  | "challenge"
  | "session"
  | "human-question"
  | "frozen"
  | "boundary";

/** SF-05 (doc 26 §13, §28): a bounded second group — revealed on attention (login) and as ambient depth. */
const DENSE_PARTICLES: readonly { x: number; y: number; r: number; d: number }[] = [
  { x: 240, y: 300, r: 1.0, d: -9 },
  { x: 520, y: 140, r: 0.9, d: -27 },
  { x: 760, y: 560, r: 1.2, d: -41 },
  { x: 1020, y: 210, r: 0.8, d: -55 },
  { x: 1320, y: 420, r: 1.1, d: -13 },
  { x: 1560, y: 120, r: 0.9, d: -70 },
  { x: 1640, y: 620, r: 1.0, d: -33 },
  { x: 420, y: 860, r: 0.9, d: -49 },
  { x: 940, y: 900, r: 1.1, d: -21 },
  { x: 1400, y: 940, r: 0.8, d: -63 },
];

const PARTICLES: readonly { x: number; y: number; r: number; d: number }[] = [
  { x: 120, y: 160, r: 1.3, d: 0 },
  { x: 860, y: 90, r: 1.1, d: -23 },
  { x: 1500, y: 240, r: 1.4, d: -47 },
  { x: 300, y: 720, r: 1.0, d: -61 },
  { x: 1180, y: 640, r: 1.2, d: -18 },
  { x: 1700, y: 820, r: 1.0, d: -80 },
  { x: 620, y: 420, r: 0.9, d: -35 },
  // human direction: a few more living particles across the whole field (same opacity-only twinkle, staggered)
  { x: 60, y: 480, r: 1.0, d: -7 },
  { x: 380, y: 60, r: 0.9, d: -52 },
  { x: 700, y: 260, r: 1.2, d: -29 },
  { x: 980, y: 520, r: 0.9, d: -66 },
  { x: 1260, y: 90, r: 1.1, d: -12 },
  { x: 1420, y: 520, r: 1.0, d: -44 },
  { x: 1760, y: 380, r: 1.2, d: -85 },
  { x: 180, y: 940, r: 1.1, d: -58 },
  { x: 560, y: 780, r: 0.9, d: -3 },
  { x: 1080, y: 860, r: 1.0, d: -38 },
  { x: 1600, y: 960, r: 0.9, d: -71 },
  { x: 820, y: 640, r: 0.8, d: -24 },
];

export function FieldBackground({ regime }: { readonly regime: BackgroundRegime }) {
  return (
    <div className="field-bg" data-regime={regime} aria-hidden="true" data-testid="field-background">
      <div className="nebula nebula-a" />
      <div className="nebula nebula-b" />
      <div className="nebula nebula-c" />
      {/* human direction: a fine irregular star layer (one static tile) and two quiet nebular veils */}
      <div className="starfield" />
      <div className="nebula nebula-d" />
      <div className="nebula nebula-e" />
      <svg className="traces" viewBox="0 0 1000 1000" focusable="false">
        <g className="drift">
          <circle cx="500" cy="500" r="300" fill="none" stroke="rgba(134,171,255,0.16)" strokeWidth="1" strokeDasharray="3 14" />
          <circle cx="500" cy="200" r="3" fill="rgba(88,220,255,0.5)" />
        </g>
        <g className="drift drift-2">
          <circle cx="500" cy="500" r="430" fill="none" stroke="rgba(88,220,255,0.1)" strokeWidth="1" strokeDasharray="2 22" />
          <circle cx="930" cy="500" r="2.5" fill="rgba(134,171,255,0.55)" />
        </g>
        <g className="drift drift-3">
          <ellipse cx="500" cy="500" rx="560" ry="380" fill="none" stroke="rgba(134,171,255,0.08)" strokeWidth="1" />
          <circle cx="500" cy="880" r="2" fill="rgba(88,220,255,0.4)" />
        </g>
      </svg>
      <svg className="particles" viewBox="0 0 1800 1000" preserveAspectRatio="xMidYMid slice" focusable="false">
        {PARTICLES.map((p, i) => (
          <circle key={i} className="particle" cx={p.x} cy={p.y} r={p.r} style={{ animationDelay: `${p.d}s` }} />
        ))}
        <g className="particles-dense">
          {DENSE_PARTICLES.map((p, i) => (
            <circle key={i} className="particle" cx={p.x} cy={p.y} r={p.r} style={{ animationDelay: `${p.d}s` }} />
          ))}
        </g>
      </svg>
    </div>
  );
}
