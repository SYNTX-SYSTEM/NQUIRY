# SFE proof-execution observability contract — SFE-PEO/1

**Status:** canonical contract and its single implementation, owned by the ORANGE proof-infrastructure Field
(this lineage). Proven at the radius stated in §9. The Level-1 binding in the SFE governing architecture
(`docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md`) is **not** made here; see §8.

## 1. Why this is a system-wide relation

Reconstructed 2026-10-05 from the repository, not assumed:

- Every SFE Field executes long-running proofs (20 §12 ladder L3–L8). The observer of such a run is the same in
  every Field: the human or agent operating it, who must tell RUNNING from STALLED before the run ends.
- The relation is Field-independent. Example consumer: PURPLE's closure regression runner
  (`auth-identity: scripts/auth_regression_run.sh`) captures the whole live pytest run in a shell variable and
  prints its evidence block only afterwards. Its recorded closure run took 31:30 with no output in between. The
  opacity comes from the shape "capture, then report", which any Field's runner may have.
- Until now the only observability lived in ORANGE's chain helper (`progress.sh`), sourced by
  `final_closure.sh` and combined there with ORANGE's own verdict aggregation and exit mapping. No other Field
  can consume that without copying it or adopting ORANGE's proof semantics.

So proof-execution observability is SFE infrastructure with many consumers and one producer, not an ORANGE
implementation detail.

## 2. Laws (unchanged from the proven ORANGE semantics)

1. Progress and heartbeat are observations, never verdicts. No event says PASS.
2. The child's real exit status is authoritative. The observer returns it unmapped.
3. Long-running stages stay reconstructable: a stage has a start event, liveness events while it runs, and
   exactly one terminal event carrying the real exit code.
4. The consuming Field keeps its own proof semantics and authority. The observer knows nothing about tests,
   verdict lines, partitions, databases or evidence formats.
5. The observer never signals, stops, retries or reorders the proof, and a failing event sink never changes
   what runs or what is returned.

## 3. Producer / consumer boundary

| | Producer (ORANGE) | Consumer (any SFE Field) |
|---|---|---|
| Owns | this contract, `sfe_observe.sh`, the event grammar in `progress.sh`, their falsifiers | its proof commands, its verdicts, its evidence, its exit conjunction |
| Provides | process facts about one child command | the command to run; optionally a stage name and a progress log |
| Never does | interpret the child's output, emit a verdict, alter streams / status / environment | parse events to derive a verdict; copy the implementation into its tree |

Interface (the whole of it):

```
sfe_observe.sh [--stage NAME] [--progress-log FILE] [--events FILE] -- COMMAND [ARG...]
```

- Exit status: the child's (128+n if a signal ended it). `2` only for a usage error of the observer, in which
  case nothing ran and no event was emitted.
- Child: foreground; stdin, stdout, stderr, arguments, working directory and environment untouched (`SHLVL` is
  one higher, as under any wrapper shell). No extra descriptor reaches it.
- Events: one line each, `[HH:MM:SS] EVENT  key=value ...`, time = elapsed since the observer started, never
  proof truth. Sink: stderr, or the file named by `--events` (appended). Never stdout, so a consumer that
  captures stdout as evidence gets it byte-identical.

| Event | Fields | Meaning |
|---|---|---|
| `STAGE_START` | `stage` | the child is about to run |
| `HEARTBEAT` | `stage`, `elapsed`, optional `pytest_progress` | the observer and its stage are alive; with `--progress-log`, the last `[ NN%]` seen in that file |
| `STAGE_END` | `stage`, `rc=0`, `elapsed` | the child exited 0 (a process fact, not a verdict) |
| `STAGE_FAIL` | `stage`, `rc=N`, `elapsed` | the child exited nonzero |
| `STAGE_TIMEOUT` | `stage`, `rc=124`, `elapsed` | the child exited 124 |

The command line is never echoed. Values outside a safe character set, and credential-like keys or values, are
replaced by `<redacted>`. Interval: `SFE_HEARTBEAT_SECONDS` (default 30).

Reconstruction rule: a `STAGE_START` without a terminal event means the observer ended before the child did
(it was terminated or killed). The observer then exits nonzero and the proof keeps running; nothing may be
concluded about the proof from the events.

## 3A. Secret / evidence boundary (provider-neutral)

Application and provider credentials may legitimately exist in a consumer's process environment, under any name
and for any provider. Two sides, kept apart:

- **Child environment: preserved.** The observer passes the environment to the child unchanged, credentials
  included. It never filters, renames or inspects it.
- **Evidence and lineage: no environment value, ever.** Events carry a stage name, an exit code, elapsed time and
  an optional progress percentage, nothing from the environment and nothing from the command line. Proofs of
  this contract show environment preservation by variable NAMES and one digest, never by persisted values. The
  contract's own falsifiers run under `env -i` with a fixed allowlist plus a fixture credential, so no ambient
  credential enters the proof process at all, and they fail if the fixture value reaches any evidence file.
- **Publication gate:** `evidence_secret_gate.py` fails if the value of any variable of the current environment
  occurs in a file that would be versioned. It knows no provider and no variable name, compares in memory, and
  reports variable name and file only. It reads no `.env` file. Run it before every lineage commit.

A consumer Field that persists its own evidence owns the same boundary for that evidence; the observer adds
nothing to it.

## 4. Ownership and location

- Owner: ORANGE, the proof-infrastructure Field. Authoritative home: branch `orange-proof-lineage`, files
  `sfe_observe.sh` + `progress.sh` (the complete closure), `evidence_secret_gate.py` and this document.
- The lineage is an orphan branch that is not an ancestor of any product branch, so it can be consumed from
  every Field without a merge and without becoming part of any proof target.
- Consumption is by reference to a lineage commit, never by copy:
  - on this machine: `worktrees/orange-proof-lineage/sfe_observe.sh`;
  - anywhere the repository is available: extract the two files of a pinned commit to a temporary directory,
    e.g. `git archive <lineage commit> sfe_observe.sh progress.sh | tar -x -C "$tmp"`.
- A Field records which lineage commit observed a run if it wants that in its provenance. The events are not
  proof evidence and need not be kept.

## 5. Adoption path (nothing here has been applied to any Field)

- **Level A, no Field change:** the operator prefixes the Field's existing proof command, for example
  `sfe_observe.sh --stage closure_regression -- bash scripts/<field runner>.sh`. Gives start, heartbeat with
  elapsed time, and the real exit status. Does not give progress inside an opaque capture.
- **Level B, the Field's own Work Unit and authority:** the Field's runner observes its inner stages (nested
  observation composes) and/or writes its pytest output to a file named with `--progress-log`.
- **Level C, Level-1 binding:** see §8.

Adoption is each Field's decision. No Field is modified by this contract.

## 6. Compatibility

- ORANGE chain: `final_closure.sh` and `progress.sh` are byte-identical to the last proven commit. The chain
  keeps emitting to stdout and keeps its own `PROOF_START` / `VERDICT` / `PROOF_END` layer; those three are
  ORANGE proof semantics and are deliberately not part of SFE-PEO/1.
- One implementation: `sfe_observe.sh` sources `progress.sh` and uses only its stage-observation subset
  (`prog_begin`, `prog_end`). It installs no exit trap of the chain and no verdict machinery.
- Existing Field runners are unaffected until they are invoked through the observer.
- Version: `SFE-PEO/1`. A change to the event names, the fields above, the sink rule or the exit rule is a new
  version. Additional optional fields are not.

## 7. What it does not do

- It does not make an opaque capture transparent: under Level A a hung child and a working child both show
  heartbeats. Heartbeat proves the observer and its stage are alive, nothing more.
- It does not persist or validate evidence, and it does not replace a Field's own tree / environment / database
  preservation checks.
- It is a bash implementation for POSIX hosts. Frontend lanes (Playwright, vitest) can be observed as a child
  command like any other; nothing frontend-specific exists.

## 8. Level-1 binding

**Done (2026-10-06).** Human Authority accepted SFE-PEO/1 as a system-wide Level-1 relation. The binding is
`20_SYSTEM_FIELD_ENGINEERING.md` §12A with `16_DECISION_GAP_REGISTER.md` §41 REC-033, committed on `pfc-integration`
(`0885ebf`), the reconstructed authoritative lineage of those documents (`evidence/ORANGE_PROOF_STATUS.md` §18).
The text below is the proposal as it was recorded before placement; §12A as committed is the authoritative wording.

### 8a. Boundary as recorded before the binding (historical)

SFE's governing architecture is `docs/architecture/20_SYSTEM_FIELD_ENGINEERING.md`. Making observability a
Level-1 law means amending that document. This lineage does not do it, for two reasons found in the repository:

- The document has no single authoritative copy at present. Two versions exist across the branches: `master` and
  `frontend-symbiotic` carry one (without §15B and the F04 successor note); `f04-implementation`,
  `auth-identity`, `pfc-integration` and `swu-px-03-worker-readiness` carry the other. `master` has not moved
  since 2026-09-26.
- Every existing change to that document was a recorded Human decision, and placing the amendment on any product
  branch modifies a consumer Field or the stale trunk.

Checked 2026-10-06: the two versions sit on two branch lines that do not contain each other (`f04-implementation`
and its descendants; `master` and the frontend branches), and both have §12 and §13 once and no §12A.

Proposed amendment text, to be placed by Human Authority (suggested: a new section after §12):

```text
## 12A. PROOF EXECUTION OBSERVABILITY

A long-running proof is observable while it runs. Observation is infrastructure, not proof:

- progress and heartbeat are observations, never verdicts;
- the real exit status of the proof process stays authoritative;
- a long-running stage is reconstructable from its start, liveness and terminal events;
- the Field keeps its own proof semantics and authority.

One canonical contract exists: SFE-PEO/1, owned by the ORANGE proof-infrastructure Field
(branch `orange-proof-lineage`, `SFE_PROOF_OBSERVABILITY_CONTRACT.md`, `sfe_observe.sh`). A Field consumes it
by reference. It does not copy the implementation and does not build its own.
```

## 9. Proof and claim ceiling

Proof: `sfe_observe_falsifiers.sh`, `evidence/sfe_observability/`; results in
`evidence/ORANGE_PROOF_STATUS.md` §16. Synthetic children only, including a consumer-shaped runner. No product
test, no product tree, no database; no consumer Field was read for execution, modified or run.

Claim ceiling: SFE-PEO/1 = ONE CANONICAL, FIELD-NEUTRAL OBSERVATION CONTRACT, PROVEN ON SYNTHETIC CONSUMERS AND
CONSUMABLE BY REFERENCE. Not claimed: adoption by any Field, observation of a real Field proof run, Level-1
status in document 20, progress visibility inside an opaque capture.
