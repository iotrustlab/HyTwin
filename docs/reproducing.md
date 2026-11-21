# Reproducing the reconstruction

This guide describes the **new executable reconstruction**. The [paper map](paper-map.md) identifies which original paper results remain unavailable. The [formal guide](formal-models.md) documents the separate machine-checked dL models.

The companion [OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate the experimental traces for HyTwin's water-treatment evaluation. Its [experimental infrastructure guide](experimental-testbed.md) links PLC projects, attack scripts, and trace collectors. The commands below generate the local synthetic demonstration; they do not execute the companion hardware workflow.

## Fast path

```bash
python3 --version                 # 3.10 or newer
python3 -m hytwin demo --output results/demo
bash check_all.sh
```

The Python path uses only the standard library and finishes in seconds. It does not open network connections or operate a PLC. Existing historical scripts are not invoked. The default `check_all.sh` runs numerical, scenario, provenance, and shell checks. If `KEYMAERAX_JAR` is set, it also replays the pinned prover obligations; otherwise it explicitly reports that prover replay was skipped.

## Models and execution order

The physical state is `(x1,x2)`; binary commands are `(v1,v2,p2)`. Rates are in **illustrative level units/second**, not unconverted volumetric SWaT measurements:

```text
q12 = v2 * p2 * transfer
x1' = v1 * inflow - q12
x2' = q12
```

Each fixed 0.25 s scan executes sensing with truthful readings, the Example 1 controller, a persistent attack overwrite if active, a latched trusted intervention if due, then exact affine evolution. The nominal scenario selects fixed flows and a fixed scan duration from the nondeterministic nominal model. Attacked scenarios use the explicit overwrite and intervention order described here; no verified implementation-refinement relationship between the Python runner and the dL models is claimed. Trusted intervention sets all three commands to zero every subsequent scan, preventing both transfer and inflow while the attacker continues attempting overwrites.

The controller retains previous commands unless a guard changes them. `low1/low2` are low triggers. The printed paper uses `high1/high2` as startup bounds, while its actual upper switching guards use the remaining one-scan margin to `HH`. The code preserves that distinction. Tank 2 has no modeled drain, so indefinite nominal safety can include a stopped process; safety is not an availability or throughput guarantee.

For transfer scenarios, the demo additionally supplies tank 1 whenever its one-scan upper margin allows inflow. That is an explicit chosen operating mode to illustrate the transfer attack, not a recovered hardware controller. The nominal initial state `(4,4,0,0,0)` satisfies the reconstructed paper startup condition. Transfer scenarios start from the safe operating state `(7,6,1,0,0)`, which is not the paper's all-actuators-closed startup state.

The plant is allowed to exceed the **safety bounds** so violations remain observable; values are not clipped to `[LL,HH]`. A run stops at a zero-level physical boundary if continuing would make a tank negative, matching the intended nonnegative evolution domain. The result reports this as `physical-domain-boundary`, with the actual completed duration. Levels above `HH` are mathematical overflow-level extrapolations: the model contains no spill dynamics or capacity cap. It therefore diagnoses violation without predicting the subsequent real-world spill volume.

## Chosen parameters and expected results

These values are selected for this demonstration, **not recovered calibration or original evaluation parameters**:

| Parameter | Value |
| --- | --- |
| Safe level interval `[LL,HH]` | `[1,12]` |
| Low/high startup thresholds, both tanks | `4 / 7` |
| Inflow level rate | `0.5` units/s |
| Transfer level rate | `0.4` units/s |
| Scan duration | `0.25` s |
| Attack onset | `2` s |
| Main scenario duration | `20` s |
| Timely / late response delays | `2 / 16` s |

| Scenario | Maximum `x1` | Maximum `x2` | Safe throughout? |
| --- | ---: | ---: | --- |
| nominal | 6.00 | 12.00 | Yes |
| direct-unmitigated | 15.00 | 6.00 | No |
| direct-mitigated | 7.00 | 6.00 | Yes |
| transfer-unmitigated | 9.80 | 13.20 | No |
| transfer-mitigated | 8.20 | 6.80 | Yes |
| transfer-late | 9.60 | 12.40 | No |

At direct-attack onset `x1=6`, so the held-command horizon is `(12-6)/0.5=12` s. The upper boundary is reached at absolute time `14` s. At transfer-attack onset `x2=6`, so the receiving-tank horizon is `(12-6)/0.4=15` s and the boundary occurs at `17` s. Tank 1 does not impose an earlier bound in that selected mode.

## Response timing and boundary behavior

An attack is injected on the first scan at or after `attack_at`. The demo knows the injected window and evaluates its matching command signature there. `signature_observed_at_s` records that observation. The response delay begins at that sampled observation, and intervention occurs on the first scan at or after `observation + requested_delay`. This is a controlled response-timing experiment, not a learned or evaluated detector. A matching command outside an injected attack could be benign.

For example, with a 0.25 s scan, requested attack time `2.1` means actual onset `2.25`. A response delay `0.3` means intervention at `2.75`, giving an actual response delay of `0.5`. Report both actual event times and requested settings when interpreting custom runs.

The safety interval is closed: reaching `HH` is safe. Continuing positive inflow after that instant is unsafe. The reported `violation_boundary_time_s` is the infimum of unsafe times, calculated within the constant-rate segment, rather than the timestamp of the first unsafe sample. A terminal state exactly on `HH` is safe if no later unsafe evolution occurs. Late shutdown freezes the state and cannot retroactively make a violating run safe.

The implementation uses Python floats and absolute safety-comparison tolerance `1e-10`; it is not an exact-real implementation of the dL semantics. The residual helper uses strict floating-point comparison, so decimal rounding near a threshold can change its verdict. The formal sensor-band proof is about exact reals. Deployment would need a numerical and measurement-error policy.

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Settings, provenance, event times, safety outcome, extrema, held-command horizon, final state, completion status |
| `traces.csv` | All six scenarios; time, physical levels, actuator commands, attack/mitigation flags, event, safety verdict |
| `delay-sweep.csv` | 81 transfer-attack response delays from 0 to 20 s, sampled in 0.25 s steps, run for 24 s |
| `overview.svg` | Standalone vector comparison of the two attack families |
| `manifest.json` | SHA-256 hashes of the four generated files plus provenance |

Trace rows include `initial`, a command state at each scan boundary, and `plant-end`. Duplicate timestamps intentionally show discrete command transitions before physical evolution. The final `plant-end` is the terminal physical state. Trace times are rounded to ten decimals for CSV readability; state evolution uses the underlying float duration. JSON has schema version 1; an absent/unbounded horizon is `null` with a separate status field, avoiding nonstandard `Infinity` values.

The built-in delay sweep has a sharp cutoff: responses through 15 s are safe in this idealized mode, and later responses violate safety. This cutoff is not a general threshold for a physical ICS. A held-command horizon predicts behavior only while its rates and commands remain valid; it is not a proof over every future flow or controller choice.

To verify deterministic outputs without changing the checked-in evidence:

```bash
python3 -m hytwin demo --output results/local/fresh
diff results/demo/manifest.json results/local/fresh/manifest.json
```

## Custom experiments

```bash
python3 -m hytwin run --attack transfer --delay 2 --output results/local/timely
python3 -m hytwin run --attack transfer --delay 16 --output results/local/late
python3 -m hytwin run --attack direct --unmitigated --output results/local/direct
python3 -m hytwin run --attack transfer --transfer 0.6 --scan 0.5 --delay 10 --output results/local/faster-flow
```

Use `python3 -m hytwin run --help` for all options. Custom runs emit a summary and trace. An unsafe outcome is an expected experimental result and the command still exits successfully; invalid input exits nonzero. Large-duration runs are capped at one million scans. The output completion status matters if a tank reaches its physical zero boundary early.

## Verification and boundaries

The Python suite checks water conservation, one-scan controller behavior across varied states, response sampling, exact analytic deadlines, late-intervention failure, repeated trusted override, physical-domain termination, invalid inputs, deterministic report hashes, and historical-file integrity. These are numerical regression tests, not substitutes for dL proofs.

The separately replayed formal artifacts prove nine obligations about idealized mathematical models. Those proofs are not inferred from passing simulations. See [formal-models.md](formal-models.md) for exact assumptions, solver version/checksum, proof status, and the remaining gap to a general shielded-system implementation.

The minimal Docker image has no Java or historical hardware dependencies. GitHub Actions checks the Python artifact; a separate manual workflow replays the pinned formal proofs. Docker availability depends on your local daemon. Container builds are a convenience path, not a claim of bit-identical operating-system images.
