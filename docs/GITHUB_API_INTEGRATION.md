# FRAMEFORGE GitHub API integration — read-only CI diagnostics

This optional utility calls GitHub's REST API to inspect repository metadata,
available GitHub Actions workflows, and recent workflow runs. It is useful during
FRAMEFORGE source import, when a workflow exists but has not run.

Run from the repository root:

```bash
python scripts/github_ci_health.py --repo SKYDRAGO-DEV/valcier-frameforge
python -m unittest discover -s scripts -p 'test_github_ci_health.py' -v
```

For private repositories, set `GH_TOKEN` in your local environment using a
read-only token with necessary repository and Actions permissions. Never store
the token in Git or paste it into issue logs. Public repositories need no token.
The utility only sends GET requests; it cannot start jobs, configure GitHub
Actions, enable achievement visibility, or claim awards.

This is a genuine GitHub API integration in development. GitHub Developer Program
membership still requires the account owner to register and provide an appropriate
support contact email. Merely installing or using this tool does not grant a badge.

Official programme requirements:
https://docs.github.com/en/integrations/concepts/github-developer-program
