# Presenting HyTwin as a research portfolio

## The central story

**HyTwin: Formal Safety Analysis and Timed Security Interventions for Industrial Cyber-Physical Systems.**

Use this as a descriptive subtitle. Keep the publication's exact title in the citation: *HyTwin: Hybrid Program Semantics for Digital Twin-Based Security Interventions in Industrial Control Systems*, Jainta Paul, Stefan Mitsch, and Luis Garcia, NFM 2025, pp. 294–312. [Published paper](https://doi.org/10.1007/978-3-031-93706-4_17).

The memorable research question is: **When must a digital twin intervene to preserve physical safety during an attack?** This connects an adversary's control over sensors and actuators to the physical consequence, the available response time, and the assumptions under which a countermeasure works. It gives a reviewer a concrete technical question to investigate in the repository.

Lead with the connection between **formal verification and experimental CPS security**. The companion **[OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main)** was used to **collect and validate the process traces for HyTwin's water-treatment evaluation**. It makes the experimental side visible through PLC projects, physical I/O integration, attack scripts, and trace acquisition tooling. [Experimental infrastructure guide](experimental-testbed.md).

The paper supplies the research contribution and its reported miniSWaT evaluation. This repository supplies surviving models, 44 recovered development files, an executable reconstruction, and **nine newly reconstructed proof obligations checked by KeYmaera X 5.1.2 with Z3**. Those proofs include unbounded nominal two-tank loop safety and fixed-flow horizon properties. The combined research story spans **mathematical modeling, machine-checked reasoning, and experimental trace collection and validation**; the [paper map](paper-map.md) identifies the evidence for each part.

## Portfolio description

> **HyTwin connects formal verification with experimental industrial security.** Published at NFM 2025, the work models adversarial sensor and actuator behavior and derives mitigation horizons for safety-preserving digital twin interventions. The companion [OpenPLC water-treatment testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate the evaluation traces, connecting the formal analysis to PLC-driven process behavior. This artifact adds nine machine-checked reconstructed proof obligations and an executable demonstration of timely versus delayed intervention. Together, the repositories make the chain from attack capability to physical consequence and response deadline inspectable.

For a short project card:

> **HyTwin — formal verification meets experimental CPS security.** NFM 2025 research connecting attack models and intervention deadlines with water-treatment trace collection and validation, supported by nine machine-checked reconstructed proof obligations.

For a GitHub description:

> NFM 2025 CPS security research: formal attack models, mitigation horizons, nine reconstructed KeYmaera X proofs, and companion PLC trace collection and validation infrastructure.

Suggested repository topics: `cyber-physical-systems`, `industrial-control-systems`, `formal-methods`, `hybrid-systems`, `differential-dynamic-logic`, `digital-twin`, `runtime-monitoring`, `security`, `keymaerax`.

## Resume wording

Publication bullet, supported by the author list and paper:

> First author of **HyTwin (NFM 2025)**, a formal framework for modeling ICS attacks and digital twin interventions using differential dynamic logic, including mitigation horizons for reasoning about response timing.

Artifact bullet, supported by the reconstruction in this repository:

> Reconstructed and machine-checked nine hybrid-system proof obligations in KeYmaera X, including nominal two-tank loop safety and fixed-flow mitigation-horizon properties; built an executable demonstration of timely and delayed security interventions.

Experimental research bullet, supported by the paper and the identified companion infrastructure:

> Connected formal attack and mitigation analysis with trace collection and validation on an OpenPLC water-treatment testbed, investigating how intervention timing affects physical safety under actuator compromise.

Adapt the first-person account of implementation to the work you personally performed. The author list supports first authorship; it does not establish who implemented every historical component.

## Tailor the emphasis to the audience

| Audience | Lead with | Show as evidence |
| --- | --- | --- |
| Formal methods and verification researchers | Hybrid programs, invariants, monitor conditions, and timing assumptions | [Formal model notes](formal-models.md), the nine reconstructed `.kyx` obligations, and [checked proof logs](../results/proofs/checked/) |
| CPS and control researchers | Coupling PLC decisions to continuous dynamics and physical safety bounds | The two-tank model, the effect of flow on the available response time, and the receiving tank's capacity |
| Systems security researchers | Adversarial actuator control, process instrumentation, and the physical consequences of delayed response | The companion [attack and trace tooling](experimental-testbed.md), explicit threat assumptions, and safe versus late mitigation traces |
| Research engineering teams | Turning a paper into a runnable and reviewable artifact | The dependency-free CLI, machine-readable results, regression checks, and recovered-file provenance |

Describe the work as **formal methods for CPS security** or **physics-aware safety analysis under attack**. A useful specialist phrase is **mitigation-horizon analysis for digital twin interventions**. Keep the water-treatment case study prominent: it makes the abstract formalism concrete.

## A three-minute walkthrough

1. State the question: "An attack is detected, but how much response time remains before a physical safety condition fails?"
2. Run the artifact from the repository root:

   ```bash
   python3 -m hytwin demo --output results/demo
   ```

3. Open `results/demo/overview.svg`. Explain the forced-actuator behavior, timely intervention, and delayed intervention for the two attack families. State that all displayed traces are newly generated illustrative simulations.
4. Show the nominal baseline in `results/demo/summary.json` and `results/demo/traces.csv`, alongside the reported attack outcomes and underlying values.
5. Open [the formal models](../models/) and [checked proof logs](../results/proofs/checked/). Explain one assumption behind the deadline: with constant positive inflow and no outflow, the remaining time to the upper bound is `(HH - x1) / f1`. The pinned replay command is `./scripts/check_models.sh --download --prove`.
6. Open the companion [water-treatment repository](https://github.com/iotrustlab/miniwatertreatment/tree/main). Show the PLC projects and trace collectors used to collect and validate the experimental traces. Explain that the displayed local demo is synthetic; the companion provides the experimental infrastructure, while the exact original Figure 2/3 recordings are not packaged in this checkout.

Use `direct-*` scenarios for the paper's running example involving `v1`. Use `transfer-*` scenarios for the Section 5 pattern involving `p2` and `v2`. This avoids conflating two different attacks.

## Answering likely interview questions

**What is the research contribution?**

The paper relates formal attack programs, mitigation programs, and runtime observations, and makes the time available for an effective intervention an explicit object of analysis. Explain the relevant definitions before discussing the implementation.

**What does running the demo establish?**

It establishes the behavior of the implemented scenarios and supports inspection of the timing argument. Simulation traces and passing regression checks do not establish the paper's general safety theorem. A proof needs explicit assumptions, a correct model, and a checked derivation.

The separate KeYmaera X replay checked nine reconstructed obligations: nominal two-tank loop safety; five attack-signature, mitigation, and sensor-band properties; and three fixed-flow horizon properties. Show the [verification metadata](../results/proofs/verification.json) when making that claim. These proofs concern their written models and assumptions, rather than the full abstract shield theorem or a deployed PLC implementation.

**Does the monitor prove an attack occurred?**

A transition can match an attack signature while also being compatible with benign behavior. Signature compatibility, detection coverage, and malicious attribution are different claims. The reconstruction exposes the modeled signature without treating it as proof of malicious intent.

**What did you recover?**

Point to the [historical recovery manifest](../legacy/recovered/manifest.json), [recovery audit](history-recovery.md), and surviving archive. The recovery restored 44 historical files, including attack models, Structured Text fragments, prototypes, and campaign logs. Describe them as development artifacts with traceable Git provenance. The relationship of each recovered file to the final publication needs evidence; the dates alone cannot establish that relationship.

**How do the formal and experimental repositories complement each other?**

HyTwin makes the attack models, safety conditions, and intervention deadlines explicit. The companion [miniwatertreatment repository](https://github.com/iotrustlab/miniwatertreatment/tree/main) provides the experimental platform used to collect and validate the process traces: PLC controller projects, hardware I/O integration, attack scripts, and Modbus acquisition. That combination shows the ability to connect mathematical reasoning with instrumented CPS experiments. The local synthetic demonstration adds an accessible way to explore the timing argument; the exact original recordings remain a separate archival requirement for complete experimental reproduction.

## Claims to keep precise

| Supported phrasing | Additional evidence needed for a stronger claim |
| --- | --- |
| "NFM 2025 publication" | NASA deployment, NASA funding, or NASA endorsement would each require separate evidence |
| "Reconstructed executable demonstration" | A complete reproduction of the paper's experiments requires the original setup details and empirical data |
| "Nine reconstructed obligations checked in KeYmaera X 5.1.2 with Z3" | The full shield theorem, implementation refinement, and real-system guarantees require additional formalization and evidence |
| "Companion OpenPLC testbed used to collect and validate HyTwin evaluation traces" | Replaying the exact published runs requires their recording files, configuration, and calibration; the current formal proofs do not certify the hardware drivers |
| "Recovered historical development artifacts" | A claim that a file was the publication's final artifact requires a matching release, record, or author confirmation |
| "Illustrative safety comparison" | Detection accuracy, latency improvements, robustness percentages, and field performance require measured experiments |

## Highest-value follow-on work

The nine replayable obligations and the existing 81-point response-delay sweep already connect the fixed-flow deadline to executable cases, while the companion testbed exposes the experimental collection and validation infrastructure. The next formal step is a reconstructed shield theorem with explicit monitor coverage and invariant-preservation conditions. Extending the analysis to bounded sensing error, actuation delay, and changing flow would test how much timing margin survives model uncertainty. Packaging experiment-specific recordings, calibration, and configurations beside the companion tooling would strengthen independent replay; any fresh experiment should retain its own date, configuration, and raw data.

A short screen recording of the existing walkthrough can make the repository easier to review in an internship application. Link the publication, the repository, and the recording together so a reviewer can move from the research claim to inspectable evidence.

## Sources

- [OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main): companion experimental infrastructure used for trace collection and validation, as identified by the HyTwin author; repository code exposes PLC integration, attacks, and trace acquisition.
- [Author-hosted paper](https://facweb.cdm.depaul.edu/smitsch/pdf/nfm25-hytwin.pdf): technical definitions, case studies, and reported miniSWaT evaluation.
- [Publisher's record](https://link.springer.com/chapter/10.1007/978-3-031-93706-4_17): authors, NFM 2025, LNCS 15682, pages 294–312, DOI, and first online date of June 8, 2025.
- [IOTrust Lab project page](https://iotrustlab.com/research/nsf-fmitf/): public research context connecting hybrid-system verification, PLCs, runtime monitoring, and HyTwin.
