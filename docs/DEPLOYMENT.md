# GitHub execution and production deployment guide

## Verified repository location
Source: https://github.com/SKYDRAGO-DEV/valcier-frameforge

GitHub Actions provides **temporary CI runners**, not continuous FastAPI hosting. GitHub Pages is static and cannot independently run this Python/SQLite backend. The included Codespaces devcontainer is the intended private-cloud development environment.

## Start a private GitHub Codespace

Select **Code → Codespaces → Create codespace on main** from your repository. In the Codespaces terminal:

```bash
bash scripts/run-codespaces.sh
```

Open forwarded port 8000. **Keep port visibility Private.** The Codespace only operates while active and is subject to GitHub's Codespaces quotas and billing. This project does not automatically create/start a Codespace.

## Locally

Python 3.11 or newer. Windows: `RUN_WINDOWS.bat`; Linux/macOS: `sh RUN_MAC_LINUX.sh`. Dashboard at http://127.0.0.1:8000. OpenAPI at http://127.0.0.1:8000/docs.

## GitHub Actions

`.github/workflows/ci.yml` installs Python dependencies, runs pytest, byte-compiles the backend, and smoke-tests `/health` and `/`. Results must be checked in GitHub **Actions**; do not infer success solely from workflow existence.

## Security

This is a deliberately constrained *local demo*. `FRAMEFORGE_LOCAL_DEMO=1` disables authentication and **must never be public-facing**. Do not make the Codespaces forwarded port public. The Dockerfile intentionally refuses to start without an API token or explicit demo flag, but the browser UI has no production login — adding a token alone does not make it safe to expose.

Required before real public hosting:
- Authentication, per-tenant authorization, secure cookies, CSRF, API throttling
- Managed Postgres with migrations and backups
- Queue workers, retries, outbox and cancellation semantics
- Provider secret management, approved commercial model contracts, webhook verification
- Signed uploads, restricted media URLs, anti-SSRF protections, audit logging
- Atomic budget reservation and real usage-price reconciliation
- User-owned content permissions and operational monitoring

There is **no real image/video generation** at v0.1; demo jobs only return JSON storyboards.
