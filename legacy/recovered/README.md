# Recovered historical artifacts

These **44 original files** were recovered from the repository's reachable Git
history on November 21, 2026. Their contents are byte-for-byte copies; they have
not been repaired or run as part of the current reconstruction. Historical paths
are preserved below this directory. See [manifest.json](manifest.json) for source
commits, deletion commits, Git blob IDs, SHA-256 hashes, sizes, and stored paths.

Most files were removed by commit `faeeb60` on March 5, 2025. Earlier formal
models and Structured Text were removed by `1629550` on November 6, 2024. A few
other paths were renamed or deleted earlier. Each restored version comes from
the parent of that path's most recent deletion, including a rename considered
as a deletion of the old path. This is an inventory of the latest deleted
versions, not an export of every historical revision.

## What is here

| Material | Location | Evidence and limitations |
| --- | --- | --- |
| Early actuator and sensor dL models | `plc_actuator_only.kyx`, `plc_sensor_only_attack.kyx` | Original attack/safety conjectures, without proof tactics or replay evidence. |
| Structured Text controller fragments | `actuator_attack.st`, `sensor_attack.st` | Original translated control fragments; no current deployment claim. |
| Attack design notes | `actuator_attack.txt`, `sensor_attack.txt`, `stealthy_actuator_attack.txt`, `stealthy_sensor_attack.txt` and older filenames | Original pseudocode and notes; several files use syntax that is not directly executable. |
| PLC and process prototypes | `Water Treatment Process/` | Python Modbus scripts, Beremiz/OpenPLC project sources and historical generated build outputs. |
| Prototype campaign logs | `Water Treatment Process/fuzzing_*_20241120_231121.txt`, `Water Treatment Process/violations_20241120_231121.txt` | Original historical logs; **not established as the data used for paper Figures 2 and 3**. |
| Exploratory monitoring | `psy-taliro.py`, `Water Treatment Process/samplemonitor.py`, `scadman_monitor/scadman_monitor_swat.py` | Historical prototypes with missing dependencies, assumptions, and known defects. The filename `psy-taliro.py` does not establish a working PSY-TaLiRo integration. |
| Historical data rewriting helper | `test.py` | Rewrites every spreadsheet in a hardcoded directory in place. Preserved as evidence; not part of the reconstruction workflow. |

## How to use this archive

Use these files to inspect the project's development history and identify
original design decisions. The current runnable demonstration and its
documentation are at the repository root. This directory is outside that
workflow. In particular, the Modbus scripts expect a configured PLC runtime,
several scripts reference the author's old computer, and compiled `.o`/`.so`
files are historical platform-specific outputs. They are preserved for complete
recovery, not offered as current executable releases.

Existing third-party copyright and license notices have been preserved,
including notices in generated OpenPLC code. Recovery does not assign a new
license or ownership to those files. No proprietary SWaT spreadsheets, Wolfram
licenses, or secrets were found among the restored files.

See [the recovery audit](../../docs/history-recovery.md) for the command history,
scientific limitations, and the distinction between recovery and reconstruction.
