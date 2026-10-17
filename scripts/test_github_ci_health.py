"""Offline regression tests for the read-only GitHub API diagnostics."""
import unittest
from unittest.mock import patch

try:
    from scripts import github_ci_health as health
except ModuleNotFoundError:
    import github_ci_health as health


class GithubHealthTests(unittest.TestCase):
    def test_valid_repo(self):
        self.assertEqual(health.check_repo_slug("SKYDRAGO-DEV/valcier-frameforge"),
                         "SKYDRAGO-DEV/valcier-frameforge")

    def test_invalid_repo_and_path_are_rejected(self):
        for repo in ("", "../secret", "a/b/other", "a/..", "a/b?foo=x", "a\\b"):
            with self.subTest(repo=repo):
                with self.assertRaises(ValueError):
                    health.check_repo_slug(repo)

    @patch.object(health, "api_get")
    def test_no_workflow_runs(self, get):
        get.side_effect = [
            {"default_branch": "main", "archived": False},
            {"total_count": 1},
            {"total_count": 0, "workflow_runs": []},
        ]
        value = health.inspect("SKYDRAGO-DEV/valcier-frameforge")
        self.assertEqual(value["recorded_run_count"], 0)
        self.assertIsNone(value["latest_run"])
        self.assertIn("No workflow runs", value["next_action"])
        self.assertEqual(get.call_count, 3)

    @patch.object(health, "api_get")
    def test_latest_failure_is_preserved(self, get):
        get.side_effect = [
            {"default_branch": "main", "archived": False},
            {"total_count": 2},
            {"total_count": 1, "workflow_runs": [
                {"name": "CI", "status": "completed", "conclusion": "failure",
                 "html_url": "https://github.com/org/repo/actions/runs/12"}]},
        ]
        value = health.inspect("org/repo")
        self.assertEqual(value["latest_run"]["conclusion"], "failure")
        self.assertEqual(value["recorded_run_count"], 1)

    @patch.object(health, "api_get")
    def test_reject_malformed_response(self, get):
        get.side_effect = [{}, {}, {"workflow_runs": "not-a-list"}]
        with self.assertRaises(ValueError):
            health.inspect("org/repo")


if __name__ == "__main__":
    unittest.main()
