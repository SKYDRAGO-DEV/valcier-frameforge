# VALCIER FRAMEFORGE v0.1

Original, independently implemented cinematic shot-planning and workflow research MVP. This repository contains the FastAPI + SQLite backend, responsive browser interface, a DAG validator, demo job lifecycle, budget check and automated tests.

**Important:** This is a DEMO creative-planning engine. It **does not generate AI images or videos**. No paid AI media provider is connected.

## Get started in GitHub Codespaces

1. In this repository choose **Code → Codespaces → Create codespace on main**.
2. The devcontainer installs the Python dependencies.
3. In the Codespaces terminal run:

```bash
bash scripts/run-codespaces.sh
```

4. Go to **Ports** and open port **8000** using the forwarded-port link. **Keep visibility PRIVATE**.

GitHub Actions is automated testing, not permanent web hosting. The application only runs while your Codespace is active. Codespaces usage and billing limits may apply.

## Run locally

Python 3.11+ required.

Windows: execute `RUN_WINDOWS.bat`.

macOS/Linux: `sh RUN_MAC_LINUX.sh`.

Or run directly:

```bash
cd backend
python -m pip install -r requirements.txt
FRAMEFORGE_LOCAL_DEMO=1 python -m uvicorn frameforge.api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. API documentation: http://127.0.0.1:8000/docs.

## Modules

- **Creative Studio:** deterministic 3-shot storyboards with cinematic intent, camera movement, lens, duration and tone.
- **Workflow Canvas:** drag-positioned nodes, edge validation, cycle rejection and topological ordering. Remote media nodes remain disabled.
- **Generation Jobs:** queue, run and cancel DEMO jobs; result JSON explicitly reports `media_generated: false`.
- **Project Library:** store and inspect projects in SQLite; export structured JSON.
- **Settings & API:** provider registry and illustrative cost/budget check.
- **Tests:** 13 tests covering API, job idempotency, graph validation, authorization and smoke checks.

## Verify

```bash
cd backend
python -m pytest -q
```

CI workflow: [Frameforge CI](.github/workflows/ci.yml). See [Actions](../../actions) for current remote results.

## Maintenance and contributions

- [Contribution and local verification guide](CONTRIBUTING.md)
- [Security policy and responsible disclosure](SECURITY.md)
- [Automated dependency update proposals](.github/dependabot.yml) for Python packages and GitHub Actions; updates are not automatically merged
- [Issue tracker](../../issues) for reproducible bugs or proposed improvements (never disclose security exploits or secrets publicly)

This repository is public for demonstration and research; **public visibility alone does not grant an open-source licence**. Check the repository's actual licence status before reusing the code.

## Security and limitations

- Public repository: NEVER commit provider API keys, tokens, SQLite databases, production assets or private data.
- Demo mode bypasses API authentication and MUST NOT be Internet-facing; port 8000 must remain private.
- Running outside demo mode requires `FRAMEFORGE_API_TOKEN`, but this is still not a production-grade multi-user architecture.
- Pending for production: tenant-aware auth, managed PostgreSQL, migrations, background workers, authorized commercial media API adapters, storage, rate limiting, auditing and billing.
- No proprietary Higgsfield code, assets, weights or internal systems are included.

The project is a research MVP, not a commercial production service.
