# Experimental testbed and trace validation

**HyTwin connects formal verification with experimental CPS security.** The companion **[OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main)** was used to **collect and validate the process traces for HyTwin's water-treatment evaluation**. This experimental role was identified by the HyTwin author. The public repository makes the supporting PLC projects, physical I/O integration, attack scripts, and trace collection tooling inspectable.

Together, the two repositories connect **adversarial control, physical process behavior, and the deadline for a safety-preserving intervention**. HyTwin supplies the formal analysis; the companion testbed supplies the experimental context in which process observations were collected and validated.

## Inspect the experimental infrastructure

The companion [README](https://github.com/iotrustlab/miniwatertreatment/blob/main/README.md) describes a reduced water-treatment platform based on SWaT processes, with Raspberry Pi 4 devices running OpenPLC and hardware sensors, pumps, and valves.

| Component | Inspectable source | Research role |
| --- | --- | --- |
| PLC controller projects | [PLC1](https://github.com/iotrustlab/miniwatertreatment/tree/main/PLC1), [PLC2](https://github.com/iotrustlab/miniwatertreatment/tree/main/PLC2), [PLC3](https://github.com/iotrustlab/miniwatertreatment/tree/main/PLC3) | Controller logic, process-variable mappings, and physical I/O drivers |
| Adversarial experiments | [Attacks](https://github.com/iotrustlab/miniwatertreatment/tree/main/Attacks) | Pump, valve, and sensor manipulation examples for observing process behavior under compromise |
| Process-trace acquisition | [TraceGenerators](https://github.com/iotrustlab/miniwatertreatment/tree/main/TraceGenerators) | PLC-specific and combined collectors for sensor and actuator observations |
| Multi-PLC collection | [master_plc_monitor.py](https://github.com/iotrustlab/miniwatertreatment/blob/main/TraceGenerators/master_plc_monitor.py) | Concurrent Modbus TCP polling across three PLCs, timestamped records, and sensor/actuator channels |
| Structured acquisition | [PLC2 JSON collector](https://github.com/iotrustlab/miniwatertreatment/blob/main/PLC2/PLC2_genTrace_JSON.py) | Timestamped register and coil observations with process-stage information |
| Experimental setup | [Diagrams](https://github.com/iotrustlab/miniwatertreatment/tree/main/Diagrams) | Water-treatment architecture and hardware context |

The combined collector records flow and level-related readings, color channels, pump and valve states, dosing states, and selected process flags. Its polling loops request a 0.1 s sleep between acquisitions; this is a requested interval, not a measured real-time sampling guarantee. PLC-specific collectors also expose structured JSON acquisition. These channels make the connection between controller actions and observed process behavior available for trace-based investigation.

## The research story

1. **Model the adversary and physical process.** Hybrid programs describe how compromised control decisions affect continuous plant behavior.
2. **Analyze the intervention window.** Safety conditions and mitigation assumptions determine when a response can still be effective.
3. **Collect and validate experimental traces.** The companion OpenPLC platform provides the instrumentation used for the water-treatment evaluation.
4. **Inspect the timing outcome.** The paper examines timely and delayed intervention; this repository adds explicit reconstructed proofs and an accessible synthetic demonstration of that mechanism.

For a portfolio, this is evidence of a research workflow spanning **formal modeling, theorem proving, PLC instrumentation, adversarial experimentation, and trace-based validation**. It provides concrete entry points for reviewers interested in either formal methods or experimental systems security.

## Provenance and scope

The historical connection to HyTwin's trace collection and validation is supplied by the author. Inspection of the public code confirms the available acquisition and experiment infrastructure; no hardware experiment was run during this documentation update. The link does not imply that the current repository contains an automated validator for the complete HyTwin formal semantics, or that the hardware drivers have been formally verified.

The exact Figure 2/3 recording files, their run-specific configuration, and calibration are not packaged in this HyTwin checkout. The locally generated `results/demo/` traces remain synthetic. The nine reconstructed KeYmaera X proofs establish properties of their stated models and assumptions. These sources complement one another and should retain their individual provenance.

Companion source inspected on November 21, 2026: commit [`ffb9fd47b2896c9dbfd2b77b6ec5c1fafcd19b0f`](https://github.com/iotrustlab/miniwatertreatment/tree/ffb9fd47b2896c9dbfd2b77b6ec5c1fafcd19b0f). Links above use `main` for current navigation. This page records the inspected revision so subsequent source changes can be distinguished from the documented snapshot.
