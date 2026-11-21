# Formal models and proof status

These are new reconstructions from [the HyTwin paper](https://facweb.cdm.depaul.edu/smitsch/pdf/nfm25-hytwin.pdf), not recovered source files or archived proofs from the original experiments. The historical [`Archive/securityformalization.kyx`](../Archive/securityformalization.kyx) is preserved separately.

## What is checked

KeYmaera X **5.1.2** with its bundled **Z3** backend parsed and proved all nine reconstructed archive entries below. See the [checked proof logs and generated lemmas](../results/proofs/checked/) and [verification metadata](../results/proofs/verification.json). These are proofs about the written mathematical models under their stated assumptions; they do not certify deployed PLC code, lost experimental traces, or the full paper's shield theorem.

| File | Obligation | Status |
| --- | --- | --- |
| [`water_tank.kyx`](../models/water_tank.kyx) | Reconstructed Example 1, nominal two-tank loop | Proved with reconstructed loop invariant |
| [`attack_mitigation.kyx`](../models/attack_mitigation.kyx) | Direct actuator signature equivalence | Proved |
| Same | Closing inflow with transfer isolated preserves both tank levels | Proved |
| Same | Opening the valve restores the pump/valve command invariant | Proved |
| Same | Valve attack signature sound positive | Proved |
| Same | Lower-band sensor spoof remains within the detector tolerance | Proved |
| [`mitigation_horizon.kyx`](../models/mitigation_horizon.kyx) | Fixed-flow horizon preserves level safety | Proved |
| Same | Any later time exceeds the upper bound under continued filling | Proved |
| Same | On-time inflow shutdown preserves the level indefinitely | Proved |

The last three specialize the paper's symbolic horizon to one tank with constant positive inflow, no effective outflow, and instantaneous trusted shutdown. They do not prove a general horizon for changing flow rates, sampled sensors, actuator lag, or recurring attacks.

## Replay

Requires Java 17 or later and a POSIX/Linux environment with Bash, `awk`, `sha256sum`, and `realpath`. To download the pinned official 147 MiB JAR, validate its checksum, parse all reconstructed models, and replay the nine proofs:

```bash
./scripts/check_models.sh --download --prove
```

For an existing official JAR:

```bash
KEYMAERAX_JAR=/absolute/path/keymaerax-5.1.2.jar ./scripts/check_models.sh --prove
```

Without `--prove`, the script checks parsing only. Fresh outputs go to `results/proofs/local/`; set `PROOF_OUT` to another directory if desired. The [manual proof workflow](../.github/workflows/proofs.yml) provides opt-in replay on GitHub Actions with Java 21 and uploads its new logs and generated lemmas. Each run uses a temporary Java user home so that KeYmaera X versions do not share a lemma cache. KeYmaera X creates one generated `.kyp` lemma per archive entry. Proof success requires both a successful process exit and an explicit `PROVED` result for every requested entry.

Pinned download: [official 5.1.2 release](https://github.com/LS-Lab/KeYmaeraX-release/releases/tag/5.1.2). JAR SHA256:

```text
6e422fa3919c5e2d134558416bfc8a6d5c2e62d29e39305df610f38d18b8cd44
```

On this run, KeYmaera X reported that some optional derived arithmetic lemmas could not be populated with Z3 and continued with restricted functionality. The raw logs retain that diagnostic; all nine requested obligations still returned `PROVED`. The generated lemmas and tactics support replay with the same prover, rather than acting as an independently checked proof certificate. See the [official installation and solver documentation](https://github.com/LS-Lab/KeYmaeraX-release#installation) for other arithmetic backends.

## Nominal two-tank model

The reconstructed Example 1 uses separate true levels `x1,x2` and sampled readings `xhat1,xhat2`. Flows `f1,f2` are chosen nondeterministically in bounded nonnegative ranges on each scan. Binary valves `v1,v2` and pump `p2` retain their settings unless the controller changes them. With level rates expressed in compatible units,

```text
q12 = v2 * p2 * f2
x1' = v1 * f1 - q12
x2' = q12
```

The controller closes the first inflow if one full scan could overflow it, opens the first inflow when its low threshold is reached, enables transfer when the second tank is low, and disables transfer if one full scan could underflow tank 1 or overflow tank 2. Every scan resets `t` to zero and permits continuous evolution for any duration in `[0,eps]`.

A suitable candidate invariant is both levels in `[LL,HH]`, each actuator binary, and the fixed parameter assumptions. The reason the protection logic can preserve the level bounds is that it constrains every nonzero level rate over the whole scan:

```text
v1*f1*eps <= HH-x1
(v1*f1-q12)*eps >= LL-x1
q12*eps <= HH-x2
```

If transfer violates either latter bound, protection sets `q12` to zero. The first tank then has nonnegative inflow, and the earlier inflow guard still controls its upper bound. Tank 2 remains constant. The reconstructed loop tactic proves this invariant argument in KeYmaera X; it is a new proof, not a recovered record of the paper's original proof.

The reconstruction makes implicit physical assumptions explicit: `eps>0`, `0<=LL`, nonnegative maximum flows, and initially closed actuators. The paper's printed plant repeats `x1'` for its second tank equation and writes `t1'`; this transcription uses `x2'` and `t'` to match the described two-tank dynamics and scan clock. The original file is retained without silently applying those changes.

The model has no receiving-tank drain, nonlinear pump curve, valve travel time, pipe-pressure dynamics, network delay, or sensor noise. A flow measured as volume/time must be divided by tank cross-sectional area before being used as a level/time rate. These simplified equations do not justify conclusions about arbitrary real SWaT telemetry.

## Attack and mitigation obligations

A direct actuator attack `v1:=1` forces inflow open. Its exact observed postcondition is `vpost=1`, giving the equivalence

```text
vpost=1 <-> <v1:=1>(vpost=v1).
```

This identifies a state transition compatible with the attack program. An open valve can also result from normal operation; the predicate alone does not establish malicious intent or provide general intrusion classification.

The direct-actuator mitigation proof closes `v1` with transfer already isolated (`v2=0`). Both level rates then equal zero. Closing only inflow while an outflow pump remains active does not generally preserve the lower bound; that extra assumption is deliberate and visible in the model.

The section 4 valve obligation restores `p2=1 -> v2=1` after an attack closes `v2` while `p2=1` and `x2<H2`. This certifies a command relationship. The model contains no pressure equation, so this is not a quantitative proof of pipe-pressure or burst safety.

For the stealthy sensor example, the paper's detector is the strict predicate `abs(xhat2-xtwin2)>delta`. A spoof `xhat2:=xtwin2-delta` remains exactly on the accepted boundary for `delta>=0`. If both the twin estimate and the manipulated reading can independently differ from truth by up to `delta`, the manipulated reading can be `2*delta` away from the true level. A tolerance on measured-versus-predicted level alone is not a bound on true-versus-measured level.

## Horizon derivation and timing

For a single tank starting at level `x0`, with constant positive net level rate `q`,

```text
x(c) = x0 + q*c
 tau = (HH-x0)/q.
```

The first horizon obligation proves `LL<=x<=HH` for every ODE duration `0<=c<=tau`. The maximality obligation proves that continued filling gives `x0+q*later>HH` for every `later>tau`. The shutdown obligation then proves that setting the inflow command to zero by `tau` freezes a still-safe level.

Equality is safe for the closed upper bound `x<=HH`: reaching `HH` is not itself a violation. Continuing to fill for any positive time after that boundary is a violation. Implementations need room for observation, communication, and actuation delay before the boundary.

The division requires `q>0`. If the net rate is zero or negative and the only concern is upper overflow, there is no finite overflow time under that fixed mode. A zero-flow case must not be modeled by dividing by zero or by inventing a finite deadline. Negative rate also requires a separate lower-bound horizon. If flow may vary, a constant measured-flow formula is a prediction unless a conservative flow bound supports the guarantee.

The mitigation clock `c` accumulates physical time. The scan clock `t` resets per iteration; substituting `t` for `c` would lose the elapsed attack duration. Zero-duration hybrid-program steps also do not provide a guarantee of progress or absence of Zeno behavior.

## Executability and non-vacuity review

The assumptions admit concrete positive-flow executions. For the nominal loop, choose `LL=1`, `HH=12`, both low thresholds `4`, both high thresholds `7`, `eps=0.25`, maximum flows `F1=0.5,F2=0.4`, initial levels `x1=x2=4`, and closed actuators. A sensing choice `f1=0.5,f2=0.4` makes the controller open inflow and transfer; a full scan increases the levels by `0.025` and `0.1`. Thus the proof is not limited to stationary behavior or zero-duration scans. The permitted sensing ranges are nonempty, and the conditional guards cover both truth values.

For the horizon obligations, `LL=1`, `HH=12`, `x=x0=6`, `q=0.5`, and `tau=12` admit positive-duration evolution to the upper boundary. Continued filling to time `13` gives level `12.5`; shutdown by time `12` leaves a level at most `12` with zero subsequent level rate. The time-domain constraint `c<=tau` represents the response deadline being assumed, rather than enforcing safety directly with a domain constraint `x<=HH`. The maximality obligation is an algebraic consequence of the affine solution; it is not a reconstruction of the paper's general quantified reachability formula.

The isolated-transfer mitigation has an executable assignment and zero subsequent level derivatives; it does not rely on a failed test discarding unsafe runs. The valve mitigation likewise has an executable branch in both pump states. Its implication is intentionally unconstrained when the pump is not running. These checks establish that the useful cases are represented, while box safety proofs still do not establish scheduler progress, throughput, attack-detection coverage, or hardware executability.

## Conditions needed for a shield theorem

The paper combines a safe nominal controller, attack monitor, and effective mitigation. A reconstructed proof should keep the following obligations distinct:

1. Initial states satisfy a loop invariant `I`, and `I` implies safety.
2. Nominal scan cycles preserve `I`.
3. A matched attack admits an executable mitigation that preserves `I` through the next physical evolution.
4. Every harmful attacked transition is matched, or an unmatched transition itself preserves `I`.
5. The implementation executes the chosen mitigation in time through a trusted path.

The printed implication `monitor -> attack-reachability` guarantees that a positive match is compatible with the attack model. On its own it does not establish item 4: an always-false monitor also satisfies this implication. For signature coverage, one needs the converse direction over the modeled observations, or a separate proof that unrecognized behaviors preserve the invariant. For the direct assignment, this repository proves an equivalence; for the conditional valve signature it claims only the written sound-positive implication.

A deterministic conditional is encoded as `(?P; mitigation) ++ ?(!P)`; using an unconditional `?true` branch would also allow skipping mitigation when `P` holds. Existential mitigation also assumes that the implementation can choose an appropriate action; it is not a guarantee for every possible mitigation choice. These conditions explain the boundary of the current reconstructed proofs and identify concrete follow-on formalization work.
