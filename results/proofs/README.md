# Reconstructed proof evidence

`checked/` contains the raw parse/prove logs and generated `.kyp` lemmas from
KeYmaera X 5.1.2 with bundled Z3. All nine reconstructed archive entries parsed
and returned `PROVED`. These results concern the reconstructed models under
their explicit assumptions, not recovered original experiment artifacts.

[`verification.json`](verification.json) records the prover download checksum,
model checksums, exact hashes of all checked logs and generated lemmas, replay
command, and individual outcomes. See
[`docs/formal-models.md`](../../docs/formal-models.md) for assumptions and scope.

Replay into a separate folder with:

```bash
./scripts/check_models.sh --download --prove
```

By default, new outputs go to `results/proofs/local/`, preserving this recorded
run. Initialization warnings about optional derived arithmetic lemmas are kept
in the logs; each requested proof still completed. Generated lemmas and tactics
support replay with the same prover, rather than independent certificate checking.

A separate [manual GitHub Actions workflow](../../.github/workflows/proofs.yml)
provides opt-in replay on Java 21 and uploads the new logs and generated lemmas.
It does not run on every push or pull request.
