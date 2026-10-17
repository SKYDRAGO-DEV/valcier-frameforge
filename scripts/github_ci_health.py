#!/usr/bin/env python3
"""Read-only GitHub Actions readiness check for a repository.

Queries the public GitHub REST API; optionally uses GH_TOKEN for private repos.
Does not alter workflow settings, claim badges, or deploy the app.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SLUG = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def check_repo_slug(value: str) -> str:
    if not SLUG.fullmatch(value) or ".." in value.split("/"):
        raise ValueError("Expected owner/repository (letters, digits, _, ., -)")
    return value


def api_get(path: str, token: str | None = None) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "frameforge-ci-health/1.0",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request("https://api.github.com" + path, headers=headers)
    with urlopen(request, timeout=12) as response:
        result = json.load(response)
    if not isinstance(result, dict):
        raise ValueError("Unexpected API response")
    return result


def inspect(repo: str, token: str | None = None) -> dict:
    repo = check_repo_slug(repo)
    base = "/repos/" + repo
    metadata = api_get(base, token)
    workflows = api_get(base + "/actions/workflows?per_page=100", token)
    runs = api_get(base + "/actions/runs?per_page=10", token)
    entries = runs.get("workflow_runs", [])
    if not isinstance(entries, list):
        raise ValueError("Unexpected workflow_runs response")
    latest = entries[0] if entries else None
    return {
        "repository": repo,
        "default_branch": metadata.get("default_branch"),
        "archived": bool(metadata.get("archived")),
        "actions_workflow_count": workflows.get("total_count", 0),
        "recorded_run_count": runs.get("total_count", 0),
        "latest_run": ({
            "name": latest.get("name"),
            "status": latest.get("status"),
            "conclusion": latest.get("conclusion"),
            "url": latest.get("html_url"),
        } if latest else None),
        "next_action": ("No workflow runs found. Check Actions permissions and trigger conditions."
                        if not entries else
                        "Inspect the latest workflow run for detailed validation."),
        "warning": "GitHub Actions evidence is not proof of live app deployment.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="SKYDRAGO-DEV/valcier-frameforge",
                        help="GitHub owner/repo (default: FRAMEFORGE)")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(inspect(args.repo, os.getenv("GH_TOKEN")), indent=2))
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        print("GitHub API check failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
