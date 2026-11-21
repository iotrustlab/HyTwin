#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -m unittest discover -s tests -v
bash -n setup.sh check_all.sh scripts/check_models.sh
if [[ -n "${KEYMAERAX_JAR:-}" ]]; then
  bash scripts/check_models.sh --prove
else
  printf '\nPython checks passed. Prover replay skipped: KEYMAERAX_JAR is unset.\n'
  printf 'See docs/formal-models.md for pinned KeYmaera X replay and scope.\n'
fi
