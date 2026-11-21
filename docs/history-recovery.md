# Historical recovery and artifact audit

Audit date: November 21, 2026. Starting revision: `b9984ee`.

**Companion experimental infrastructure:** the HyTwin author identified [miniwatertreatment](https://github.com/iotrustlab/miniwatertreatment/tree/main) as the repository used to collect and validate the water-treatment evaluation traces. The recovery findings below concern this local HyTwin checkout and its Git history. They do not imply that experimental tooling is unavailable; see the [companion testbed guide](experimental-testbed.md).

## What was actually recovered

The files were not all lost with the old computer. The local clone contains 25
commits spanning October 17, 2024 through March 11, 2025. Its reachable history
retains **44 paths that are absent from the starting revision**, totaling
268,131 bytes. They have been restored byte-for-byte under
[`legacy/recovered/`](../legacy/recovered/), preserving their historical paths.
No current original was moved or overwritten.

The [manifest](../legacy/recovered/manifest.json) records the full source commit,
deletion commit, Git blob ID, SHA-256 content hash, byte count, and stored path
for every recovered file. Every stored file was compared with `git show` output
from its source revision and its SHA-256 hash was checked after restoration.

| History event | Recoverable material | Source before removal |
| --- | --- | --- |
| `faeeb60` (March 5, 2025) | Water-treatment prototypes, PLC project/build outputs, campaign logs, attack notes, exploratory monitoring and data helper | `a92c042` |
| `1629550` (November 6, 2024) | Two `.kyx` attack conjectures and two Structured Text fragments | `de520bf` |
| Earlier renames/removals | Original attack filenames and a TODO list | Per-file revision in manifest |

The clone has only `main` and `origin/main`; `git fsck --full --no-reflogs`
reported no dangling objects. The reflog only records the recent clone. This
audit therefore found no additional uncommitted work or unreachable historical
experiments to recover.

Recovery covers the latest deleted version of each historical path. Earlier
revisions remain available through Git; they were not duplicated into the
working tree. The original paper PDF is referenced from the README rather than
represented as a recovered repository artifact.

## Scope of the locally recovered experiment evidence

The paper's Section 5 describes two miniSWaT experiments that compromise pump
`p2` and valve `v2`, with rapid versus delayed mitigation. The restored November
2024 campaign files contain logs produced for a separate range-sensor/pump
prototype. The available files do not establish a mapping from those logs to
Figures 2 and 3, their exact experiment settings, or their measurement channels.
They should be described as **historical prototype logs**, never as recovered
Figure 2/3 measurements.

No verified original proof certificates, replayable original proof tactics,
proprietary SWaT Excel datasets, or confirmed original Figure 2/3 telemetry were
found. That absence is a limit of the available evidence, not a claim that those
artifacts never existed.

## Scientific review of the starting revision

The original [`Archive/securityformalization.kyx`](../Archive/securityformalization.kyx)
is retained. It is a historical draft rather than a trustworthy proof suite:

- **Nominal control differs from Example 1.** Its sensing does not distinguish
  true and measured levels or impose the paper's upper flow bounds. The inflow
  branch permits any nonnegative `f1` while `x1 < H1`, so large inflow can cross
  `HH` during one scan. A positive scan duration is not assumed even though the
  controller divides by `T`.
- **Several theorems omit physical evolution.** The direct mitigation and valve
  mitigation statements execute only assignments to actuators and then assert
  level safety. The water levels never change in those programs, so such a
  statement does not establish safety during a physical response. The valve
  example also modifies `V1`, whereas Section 4 attacks `v2`.
- **The mitigation clock is incomplete.** The timed attack contains a TODO,
  resets scan clock `t` each iteration, and does not evolve the mitigation
  clock `c`. A test `t <= T` alone does not characterize a derived mitigation
  horizon or account for total elapsed attack time.
- **The stealthy sensor mitigation cannot detect its stated attack.** The attack
  constrains deviation to `<= D`, while its monitor requires `> D`. Its state
  variable also mixes the reported sensor reading and physical level.
- **The sensor spike composition can be infeasible.** The attack requires
  deviation `<= E`; the immediately following mitigation tests deviation `> E`.
  That composition has no successful run, so a box safety statement can hold
  vacuously. It is not evidence of a functioning mitigation.
- **No proof tactics are included.** The archive contains theorem declarations,
  without `Tactic` blocks or proof replay evidence. Calling a declaration
  `Theorem` does not show that KeYmaera X discharged it.

The original [`scadman_monitor_swat.py`](../scadman_monitor_swat.py) is likewise an
exploratory script. It multiplies measured flow by actuator values without an
explicit actuator-code conversion, estimates level directly from flow without
documented unit/area conversion, and requires an absent Excel dataset at an
author-specific path. These features do not support a claim of a reproduced
SCADMAN implementation or validated detection results. A recovered `test.py`
rewrites spreadsheet values globally and in place; this is not a substitute
for an explicit, column-aware dataset schema.

The recovered files have not been repaired or executed. Examples of prototype
defects include inconsistent Modbus mappings between scripts, a trace parser
that indexes the outer row list instead of a row, and an exploratory attack
score that counts any nonzero level as an attack. Their archival value is their
authentic provenance; the reconstructed workflow has separate evidence.

## Recovery method

Read-only inventory commands:

```bash
git log --all --format='%h %ad %s' --date=short
git log --all --no-renames --name-status
git branch -a
git fsck --full --no-reflogs
git reflog --all
```

For each historically present path absent at the starting revision, the
recovery selected the most recent deletion with renames treated as delete/add,
then copied the file from the deletion's parent. For example:

```bash
git show a92c042:'Water Treatment Process/overflow_fuzzer.py'
git show de520bf:plc_actuator_only.kyx
```

The manifest allows recovery to be audited without trusting filenames or
new documentation. A content check can be performed with Python's standard
library:

```python
from pathlib import Path
import hashlib
import json
import subprocess

manifest = json.loads(Path('legacy/recovered/manifest.json').read_text())
for item in manifest['artifacts']:
    data = Path(item['stored_path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['blob_sha256']
    original = subprocess.check_output([
        'git', 'show', item['source_commit'] + ':' + item['original_path']
    ])
    assert data == original
```

The verification reads only; it does not execute recovered scripts or binaries.
