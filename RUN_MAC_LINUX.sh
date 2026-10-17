#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/backend"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
python -m pip install -r requirements.txt
export FRAMEFORGE_LOCAL_DEMO=1
echo 'VALCIER FRAMEFORGE LOCAL DEMO: http://127.0.0.1:8000'
python -m uvicorn frameforge.api:app --host 127.0.0.1 --port 8000
