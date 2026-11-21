# Historical material

The [`recovered/`](recovered/) directory contains byte-for-byte files restored from repository history. Its manifest records source commits and hashes. The surviving root [`Archive/securityformalization.kyx`](../Archive/securityformalization.kyx) and [`scadman_monitor_swat.py`](../scadman_monitor_swat.py) are unchanged.

The pre-reconstruction infrastructure is preserved here as:

- `Dockerfile.keymaerax`: original MATLAB-dependencies/Wolfram/Scala build.
- `setup-keymaerax.sh`: original container setup and activation script.
- `check-all-original.sh`: original checker, referring to unrelated missing model files.

These are provenance artifacts, not the supported setup path. The old setup references a missing `keymaerax.math.conf`, licensing activation, obsolete external installers, and fixed container names. The root Dockerfile/setup/check scripts now run the portable reconstruction. Do not interpret a successful new demo as validation of these historical scripts or any generated historical PLC binaries.

No confirmed original Figure 2/3 experimental telemetry or original proof-session exports were recovered from this HyTwin checkout and its Git history. The companion [OpenPLC Mini Water Treatment Testbed](https://github.com/iotrustlab/miniwatertreatment/tree/main) was used to collect and validate the evaluation traces; [its experimental infrastructure](../docs/experimental-testbed.md) is available separately. Details and scientific issues in the local drafts are in the [history audit](../docs/history-recovery.md).
