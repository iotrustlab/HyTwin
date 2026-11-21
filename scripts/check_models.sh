#!/usr/bin/env bash
# Parse reconstructed archives and optionally replay their checked proof tactics.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mode=parse
download=false
for arg in "$@"; do
  case "$arg" in
    --prove) mode=prove ;;
    --download) download=true ;;
    --help|-h)
      cat <<'USAGE'
Usage: scripts/check_models.sh [--prove] [--download]

Default: parse every reconstructed model. With --prove, also replay the
9 reconstructed nominal-loop/monitor/mitigation/horizon obligations.

KEYMAERAX_JAR   Path to the official KeYmaera X 5.1.2 JAR.
PROOF_OUT      Output folder (default: results/proofs/local).
PROOF_TIMEOUT  Timeout per proof in seconds (default: 60).

--download downloads and SHA256-verifies pinned 5.1.2 into .cache/.
Java >=17, sha256sum, and (for --download) curl are required.
USAGE
      exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done

jar_path=${KEYMAERAX_JAR:-"$repo_root/.cache/keymaerax-5.1.2.jar"}
expected_sha=6e422fa3919c5e2d134558416bfc8a6d5c2e62d29e39305df610f38d18b8cd44
if [[ ! -f "$jar_path" ]]; then
  if [[ "$download" != true ]]; then
    printf 'KeYmaera X JAR not found: %s\nSet KEYMAERAX_JAR or pass --download.\n' "$jar_path" >&2
    exit 2
  fi
  mkdir -p -- "$(dirname -- "$jar_path")"
  curl --fail --location --silent --show-error \
    https://github.com/LS-Lab/KeYmaeraX-release/releases/download/5.1.2/keymaerax.jar \
    --output "$jar_path.part"
  actual_sha=$(sha256sum -- "$jar_path.part")
  if [[ "${actual_sha%% *}" != "$expected_sha" ]]; then
    printf 'KeYmaera X download checksum mismatch.\n' >&2
    rm -f -- "$jar_path.part"
    exit 1
  fi
  mv -- "$jar_path.part" "$jar_path"
fi
actual_sha=$(sha256sum -- "$jar_path")
if [[ "${actual_sha%% *}" != "$expected_sha" ]]; then
  printf 'Expected the pinned KeYmaera X 5.1.2 JAR (SHA256 %s).\n' "$expected_sha" >&2
  exit 2
fi
jar_path=$(realpath -- "$jar_path")
out_dir=${PROOF_OUT:-"$repo_root/results/proofs/local"}
mkdir -p -- "$out_dir"
out_dir=$(realpath -- "$out_dir")
# Do not share a user's lemma cache across versions or concurrent proof runs.
prover_home=$(mktemp -d "${TMPDIR:-/tmp}/hytwin-prover.XXXXXXXX")
trap 'rm -rf -- "$prover_home"' EXIT

run_kyx() {
  java -Duser.home="$prover_home" -Xss20m -da -jar "$jar_path" -launch "$@"
}

for model in "$repo_root"/models/*.kyx; do
  model_name=$(basename -- "$model" .kyx)
  log_file="$out_dir/$model_name.parse.log"
  if ! run_kyx -parse "$model" -tool z3 >"$log_file" 2>&1; then
    cat -- "$log_file" >&2
    exit 1
  fi
  expected_count=$(awk '/^ArchiveEntry / {n++} END {print n+0}' "$model")
  actual_count=$(awk '/^Parsed file successfully$/ {n++} END {print n+0}' "$log_file")
  if [[ "$actual_count" != "$expected_count" ]]; then
    printf 'Parse result count mismatch: %s\n' "$log_file" >&2
    exit 1
  fi
  printf 'PARSED %s (%s entries)\n' "$model_name" "$actual_count"
done

if [[ "$mode" == prove ]]; then
  for model_name in attack_mitigation mitigation_horizon water_tank; do
    log_file="$out_dir/$model_name.prove.log"
    if ! run_kyx -prove "$repo_root/models/$model_name.kyx" -tool z3 \
        -timeout "${PROOF_TIMEOUT:-60}" -out "$out_dir/$model_name.kyp" >"$log_file" 2>&1; then
      cat -- "$log_file" >&2
      exit 1
    fi
    expected_count=$(awk '/^ArchiveEntry / {n++} END {print n+0}' "$repo_root/models/$model_name.kyx")
    actual_count=$(awk '/^PROVED / {n++} END {print n+0}' "$log_file")
    if [[ "$actual_count" != "$expected_count" ]]; then
      cat -- "$log_file" >&2
      printf 'Proof result count mismatch for %s.\n' "$model_name" >&2
      exit 1
    fi
    awk '/^PROVED /' "$log_file"
  done
fi
printf 'Logs: %s\n' "$out_dir"
