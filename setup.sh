#!/usr/bin/env bash
# Dependency-free default path. Original Wolfram/Docker setup is in legacy/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
python3 -m hytwin demo --output results/demo
printf '\nNext: bash check_all.sh\nFormal models: see docs/formal-models.md\n'
