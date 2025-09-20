#!/usr/bin/env python3
"""
Unit and integration tests for client.GithubOrgClient.
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class  # type: ignore
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class."""

    @parameterized.expand([  # type: ignore[misc]
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json) -> None:
        """Test that GithubOrgClient.org calls get_json once with the right URL."""
        test_client = GithubOrgClient(org_name)
        test_client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns expected value from org payload."""
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value=payload
        ):
            test_client = GithubOrgClient("google")
            self.assertEqual(test_client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """Test that public_repos returns the expected repo list."""
        test_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = test_payload

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/google/repos"
        ) as mock_repos_url:
            test_client = GithubOrgClient("google")
            result = test_client.public_repos()

            self.assertEqual(result, ["repo1", "repo2"])
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([  # type: ignore[misc]
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        """Test has_license returns True/False depending on repo license."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class([  # type: ignore[misc]
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos with fixtures."""

    @classmethod
    def setUpClass(cls) -> None:
        """Start patcher for requests.get with side_effect returning fixtures."""
        cls.get_patcher = patch("requests.get")  # keep patcher object
        mock_get = cls.get_patcher.start()       # start patcher

        def side_effect(url: str):
            """Return mock responses depending on requested URL."""
            mock_response = unittest.mock.Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Integration test for public_repos returns expected repos list."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Integration test for filtering repos by license key."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
