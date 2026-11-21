# Paper-to-artifact map

This repository accompanies Jainta Paul, Stefan Mitsch, and Luis Garcia, [*HyTwin: Hybrid Program Semantics for Digital Twin-Based Security Interventions in Industrial Control Systems*](https://doi.org/10.1007/978-3-031-93706-4_17), NFM 2025, LNCS 15682, pp. 294–312. The [author-hosted PDF](https://facweb.cdm.depaul.edu/smitsch/pdf/nfm25-hytwin.pdf) is the technical reference. Page numbers below refer to its 19 PDF pages, beginning with the title page as page 1.

## Evidence categories

| Category | Meaning in this repository | What it establishes |
| --- | --- | --- |
| **Surviving** | Files present in the starting checkout, including [the archive](../Archive/securityformalization.kyx) and the original SWaT monitor | The original file contents survived; their presence alone does not establish that they run or were the final publication artifact |
| **Recovered** | 44 development files restored from existing Git history under [legacy/recovered](../legacy/recovered/), with a [per-file manifest](../legacy/recovered/manifest.json) | Their historical contents and provenance are recoverable; their role in the final experiments is not automatically known |
| **Companion experimental infrastructure** | [OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main), identified by the HyTwin author as the repository used to collect and validate evaluation traces | Exposes the experimental PLC projects, physical I/O integration, attack scripts, and trace collectors; [infrastructure guide](experimental-testbed.md) |
| **Reconstructed** | New Python demonstration, nine machine-checked formal obligations, checks, and documentation written from the paper and surviving evidence | A new inspectable implementation and checked model-level properties, under stated assumptions |
| **Not packaged in this checkout** | Exact original Figure 2/3 recordings, run-specific configuration and calibration, and original proof-session exports | The collection and validation infrastructure is linked separately; exact experimental replay still requires these run-specific records |

The reconstruction is dated November 2026. It does not retroactively replace the publication's original experimental record. The companion [miniwatertreatment repository](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate the experimental traces; the paper's formal analysis and that experimental infrastructure form complementary parts of the research artifact.

KeYmaera X **5.1.2** with **Z3** parsed and proved all nine new archive entries: one nominal two-tank loop obligation, five attack/monitor/mitigation/sensor-band obligations, and three fixed-flow horizon obligations. The [verification metadata](../results/proofs/verification.json) records model hashes and tool versions; [raw proof logs and generated lemmas](../results/proofs/checked/) retain replay evidence. See [formal model notes](formal-models.md) for the exact assumptions and replay command.

## Historical artifacts recovered from Git

The [recovery audit](history-recovery.md) describes the source revisions, exact byte comparisons, and known defects. These recovered files provide authentic development history:

| Recovered material | Links | Supported interpretation |
| --- | --- | --- |
| Actuator and sensor attack conjectures | [Actuator `.kyx`](../legacy/recovered/plc_actuator_only.kyx), [sensor `.kyx`](../legacy/recovered/plc_sensor_only_attack.kyx) | Early formalization artifacts; no proof certificates recovered |
| PLC code fragments | [Actuator Structured Text](../legacy/recovered/actuator_attack.st), [sensor Structured Text](../legacy/recovered/sensor_attack.st) | Historical controller/attack fragments; not confirmed as deployed experiment code |
| Attack modeling notes | [Direct actuator](../legacy/recovered/actuator_attack.txt), [sensor](../legacy/recovered/sensor_attack.txt), [stealthy actuator](../legacy/recovered/stealthy_actuator_attack.txt), [stealthy sensor](../legacy/recovered/stealthy_sensor_attack.txt) | Evidence of the modeling process; not a one-to-one authenticated mapping to the final paper examples |
| Water-treatment prototypes | [Tank simulator](<../legacy/recovered/Water Treatment Process/tanksim.py>), [fuzzer](<../legacy/recovered/Water Treatment Process/overflow_fuzzer.py>), [PLC project](<../legacy/recovered/Water Treatment Process/plc2Sim/plc2sim/>) | Historical simulation and PLC integration work, preserved without modernization |
| November 2024 campaign logs | [Fuzzing summary](<../legacy/recovered/Water Treatment Process/fuzzing_summary_20241120_231121.txt>), [trace](<../legacy/recovered/Water Treatment Process/fuzzing_trace_20241120_231121.txt>), [violations](<../legacy/recovered/Water Treatment Process/violations_20241120_231121.txt>) | Historical prototype data; not established as the measurements in Figures 2–3 |

## Technical mapping

| Paper location | Technical content | Artifact or explanation | Scope and limits |
| --- | --- | --- | --- |
| Section 2.2, PDF pp. 3–4 | Hybrid programs and differential dynamic logic | Reconstructed [KeYmaera X models](../models/) and [formal model notes](formal-models.md) | Nine reconstructed obligations proved; simulation remains a separate execution path |
| Section 2.3, PDF pp. 4–5 | ModelPlex reachability monitors | [Formal model notes](formal-models.md); monitor predicates in the executable reconstruction | The Python predicates are explicit implementations, not a recovered ModelPlex synthesis session |
| Section 2.4, PDF p. 5 | PLC scan cycle normal form | [Water-tank model](../models/water_tank.kyx) and the Python scan-cycle demonstration | Demo schedules concrete scan durations; the formal model allows nondeterministic durations within the scan bound |
| Section 3.1 / Figure 1, PDF p. 6 | Known attack, monitor, signature, horizon, mitigation workflow | [README](../README.md) and executable demonstration | A small set of explicit scenarios represents the workflow; no claim of a production attack database or PLC deployment |
| Example 1, PDF pp. 7–8 | Two-tank controller, physical dynamics, assumptions, and safety bounds | [Water-tank model](../models/water_tank.kyx) | Nominal loop safety proved with a reconstructed invariant; corrections and additional assumptions are documented in [formal model notes](formal-models.md) |
| Definitions 1–3, PDF pp. 8–9 | Attack programs, attacked systems, and attack traces | [Attack and mitigation models](../models/attack_mitigation.kyx); `direct-*` and `transfer-*` demo scenarios | Concrete demonstrations sample particular behaviors, rather than exhaust the nondeterministic attack class |
| Definition 4, PDF p. 9 | Two-state attack detectors | Explicit monitor predicates and [formal model notes](formal-models.md) | Detector compatibility is distinct from attribution of malicious intent |
| Example 2, PDF p. 10 | Direct actuator attack `v1 := 1` | `direct-unmitigated` demo; [attack and mitigation models](../models/attack_mitigation.kyx) | Acts on the source tank's inflow valve; distinct from the Section 5 transfer attack |
| Definition 5, PDF p. 10 | Stealth relative to a detector set | [Attack and mitigation models](../models/attack_mitigation.kyx), Section 4 stealth-band obligation | No claim of a measured stealthy-attack detection benchmark |
| Definition 6 / Example 3, PDF p. 10 | Mitigation effectiveness and closing compromised inflow | `direct-mitigated` demo; [attack and mitigation models](../models/attack_mitigation.kyx) | Safe shutdown proved with transfer already isolated; authority over the actuator remains an explicit assumption |
| Definition 7 / Example 4, PDF p. 11 | Attack monitor and the predicate `v1+ = 1` | [Attack and mitigation models](../models/attack_mitigation.kyx) and [formal model notes](formal-models.md) | Exact signature equivalence proved for direct assignment; a benign open valve can also match, and the general shield needs a separate coverage argument |
| Definition 8, PDF p. 11 | Adding a fresh clock to continuous evolution | Clocked [horizon model](../models/mitigation_horizon.kyx) | Reconstructed for the selected specialization, rather than a general-purpose timed-program transformer |
| Definitions 9–10, PDF p. 12 | Safety horizon and mitigation horizon | [Horizon model](../models/mitigation_horizon.kyx) and executable deadline calculations | A time-to-boundary formula is a valid horizon only under its stated flow and mitigation assumptions |
| Example 5, PDF p. 12 | Fixed-positive-inflow witness `(HH - x1) / f1` with no outflow | [Horizon model](../models/mitigation_horizon.kyx); direct-attack scenarios | Safety through the horizon, later-time violation under filling, and on-time shutdown proved for the fixed-flow specialization; equality is safe for `x1 <= HH` |
| Example 6, PDF pp. 12–13 | Outflow mitigation and further intervention if draining is insufficient | [Formal model notes](formal-models.md) | Discussion and modeling caveats; no reconstructed universal proof of this entire example |
| Definition 11 / Theorem 1, PDF pp. 13–14 | Shielded system and invariant-preserving mitigation | [Formal model notes](formal-models.md) | Not claimed as a fully replayed reconstruction of the general shield theorem; monitor coverage and next-cycle invariant preservation must be established |
| Section 4, "Valve Attack", PDF p. 14 | Closed transfer valve while pump runs; force valve open | [Attack and mitigation models](../models/attack_mitigation.kyx) | Mitigation of `p2 = 1 -> v2 = 1` and a sound-positive signature proved; these command properties do not quantify pipe pressure |
| Section 4, "Stealthy Sensor Attack", PDF pp. 14–15 | Sensor perturbation within a twin-prediction tolerance | [Attack and mitigation models](../models/attack_mitigation.kyx), [formal model notes](formal-models.md) | Lower-band spoof proved to remain in the accepted tolerance; no recovered sensor calibration or real-data evaluation |
| Section 4, "Sensor Spike Attack", PDF p. 15 | False high level triggers draining; stopping before underflow | [Formal model notes](formal-models.md) | Explained as an extension; the running two-tank demo does not reconstruct an emergency-drain `p3/v3` implementation |
| Section 5 / Figures 2–3, PDF pp. 16–17 | Forced transfer pump and valve; timely versus delayed mitigation | Companion [testbed used to collect and validate the experimental traces](https://github.com/iotrustlab/miniwatertreatment/tree/main); local `transfer-*` scenarios and `results/demo/overview.svg` | Companion infrastructure supports the experimental workflow; local outputs are qualitative synthetic reconstructions, not the original plotted samples |
| Section 6, PDF pp. 16–17 | Fidelity, scan-cycle semantics, and resilient-controller synthesis as future work | [Showcase and follow-on directions](showcase.md) | These remain research directions rather than implemented capabilities of this artifact |

## Executable outputs

Run from the repository root:

```bash
python3 -m hytwin demo --output results/demo
```

| Output | Purpose | Provenance |
| --- | --- | --- |
| `results/demo/traces.csv` | Inspect the concrete simulated trajectories | Generated by the reconstructed simulator |
| `results/demo/summary.json` | Inspect scenario outcomes and configuration | Generated by the reconstructed simulator |
| `results/demo/overview.svg` | Compare attacked, timely, and late responses in the two attack families | Generated visualization of the new simulation; the nominal baseline is in CSV/JSON |

The parameter values and attack schedule are illustrative choices. They do not recover unpublished experimental settings. Physical units, clock assumptions, fixed flow, and mitigation authority should be read from the current configuration and model documentation before interpreting a numeric deadline.

## Why the original figures are not regenerated

Section 5 reports two physical miniSWaT executions and shows the timely-versus-delayed outcome. The companion [OpenPLC water-treatment repository](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate the traces, as identified by the author. Its public PLC projects and collectors expose the experimental infrastructure. The exact sampled trajectories and complete run-specific configuration are not packaged in this HyTwin checkout. A visually similar newly generated plot would not establish that the original measurements had been recovered.

The reconstructed figure therefore demonstrates the same qualitative timing mechanism using explicit chosen values. No original accuracy, overhead, detector latency, or hardware-performance number is inferred from it. Recoverable historical fuzzing logs remain historical fuzzing logs unless their relationship to the Section 5 experiment can be independently established.

## Interpreting formal claims

The printed model includes apparent typographic inconsistencies in state derivatives; the reconstructed model uses one derivative per intended state and records the decision. The [formal model notes](formal-models.md) also separate monitor soundness from coverage, explain assumptions needed for horizon calculations, and distinguish protecting the source tank from protecting the receiving tank.

A checked arithmetic obligation, a checked loop proof, and a successful numerical scenario provide different evidence. All nine current reconstructed `.kyx` obligations were proved in the [recorded replay](../results/proofs/verification.json). The full abstract shield theorem and the original prover sessions remain outside that claim. Model hashes in the verification record allow readers to check that the logs correspond to the current sources; future model edits require replay before carrying the proof claim forward.

## Sources

- [Companion OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main): experimental infrastructure used for trace collection and validation, as identified by the HyTwin author; [inspected source and role](experimental-testbed.md).
- [Author-hosted paper PDF](https://facweb.cdm.depaul.edu/smitsch/pdf/nfm25-hytwin.pdf): all section, example, definition, theorem, and figure locations in the mapping.
- [Publisher's record](https://link.springer.com/chapter/10.1007/978-3-031-93706-4_17): exact bibliographic metadata and link to this repository as the paper's artifact location.
- Local Git history, the [recovery audit](history-recovery.md), and the [recovered-file manifest](../legacy/recovered/manifest.json): provenance for recovered development files; these do not authenticate unavailable physical experiment data.
