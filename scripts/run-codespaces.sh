#!/usr/bin/env bash
set -euo pipefail
if [[ "${CODESPACES:-}" != "true" ]]; then
  printf '%s\n' 'This helper is intended for a PRIVATE GitHub Codespace.' 'For local use, run RUN_MAC_LINUX.sh.' >&2
  exit 1
fi
cd "$(dirname "${BASH_SOURCE[0]}")/../backend"
export FRAMEFORGE_LOCAL_DEMO=1
export FRAMEFORGE_DB_PATH="${FRAMEFORGE_DB_PATH:-$PWD/frameforge.db}"
printf 'Starting LOCAL-ONLY demo; Codespaces forwarded port 8000 MUST remain PRIVATE.\n'
exec python -m uvicorn frameforge.api:app --host 127.0.0.1 --port 8000
