import coreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

// eslint-config-next@16.3.5 ships native ESLint 9+ flat config arrays at
// these subpaths (see node_modules/eslint-config-next/package.json
// "exports"). Bridging them through @eslint/eslintrc's FlatCompat (the
// older Next.js boilerplate pattern, for pre-flat-config shareable
// configs) is unnecessary here and actively breaks: FlatCompat's legacy
// schema validator crashes with "Converting circular structure to
// JSON" on eslint-plugin-react's self-referencing flat plugin object
// when asked to treat this already-flat config as a classic one.
const eslintConfig = [...coreWebVitals, ...nextTypescript];

export default eslintConfig;
