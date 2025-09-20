#!/usr/bin/env python3
"""
Unit tests for client.GithubOrgClient.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized  # type: ignore
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([  # type: ignore[misc]
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json) -> None:
        """
        Test that GithubOrgClient.org returns the expected value and
        get_json is called once with the correct argument.
        """
        test_client = GithubOrgClient(org_name)
        test_client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )


if __name__ == "__main__":
    unittest.main()
