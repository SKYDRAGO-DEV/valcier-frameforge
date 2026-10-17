# Contributing to VALCIER FRAMEFORGE

Thanks for helping improve this experimental, research-oriented application.

## Scope

This repository currently implements a FastAPI + SQLite creative-planning demo with browser UI, deterministic storyboard logic, DAG validation and simulated job lifecycle. **It does not generate real images or videos.** Please do not describe disabled media-provider nodes as operational.

## Local setup

Prerequisites: Python 3.11+ and Git.

```bash
git clone https://github.com/SKYDRAGO-DEV/valcier-frameforge.git
cd valcier-frameforge/backend
python -m venv .venv
```

Activate the virtual environment using your shell's normal command, then:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q frameforge
```

For a **local-only** smoke test (never expose demo mode publicly):

```bash
FRAMEFORGE_LOCAL_DEMO=1 python -m uvicorn frameforge.api:app --host 127.0.0.1 --port 8000
```

On Windows PowerShell, set `$env:FRAMEFORGE_LOCAL_DEMO = '1'` before launching the equivalent Python command.

## Change workflow

1. Search existing issues, and open a design discussion for changes affecting architecture or API compatibility.
2. Branch from `main`; make small, reviewable changes.
3. Add or update tests for API behaviour, DAG rules, job transitions, input validation and security boundaries as applicable.
4. Run the tests and compilation checks above.
5. Update README/docs when observed behaviour, flags or limitations change.
6. Open a pull request explaining the problem, solution, validation, compatibility impact and any new dependency.

## Pull-request principles

- Never include provider credentials, customer assets, token values, private data, local SQLite files or generated media.
- Do not weaken demo-mode warnings, authentication checks or private-port guidance.
- Do not introduce an AI provider integration without documenting its authorization, cost, data retention and failure modes.
- Do not use fictitious benchmarks, tests, output screenshots or generated results as evidence.
- GitHub Actions workflows must retain least-privilege permissions and must not execute untrusted PR code with elevated credentials.

## Reporting issues

Use the repository issue templates for reproducible bugs and narrowly scoped enhancements. Security vulnerabilities should follow [SECURITY.md](SECURITY.md), **not** public issues.

Licensing and reuse must be reviewed against the repository's actual legal status; public visibility alone does not grant an open-source licence.
