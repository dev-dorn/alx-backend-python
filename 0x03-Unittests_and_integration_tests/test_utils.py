#!/usr/bin/env python3
"""
Unit tests for utils.access_nested_map using parameterized inputs.
"""

import unittest
from unittest.mock import patch, Mock
from typing import Any, Dict, Tuple
from parameterized import parameterized  # type: ignore
from utils import access_nested_map, get_json


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function."""

    @parameterized.expand([  # type: ignore[misc]
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected: Any
    ) -> None:
        """Test that access_nested_map returns expected results."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([  # type: ignore[misc]
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...]
    ) -> None:
        """Test that access_nested_map raises KeyError with correct message."""
        with self.assertRaises(KeyError) as error:
            access_nested_map(nested_map, path)

        self.assertEqual(str(error.exception), repr(path[-1]))

class TestGetJson(unittest.TestCase):
    """Unit test for the get_json function (Task 2)."""

    @parameterized.expand([ #type: ignore[misc]
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: Dict[str: Any]) -> None:
            """Test that get_json returns expected payload from mocked HTTP Calls"""
            mock_response: Mock = Mock()
            mock_response.json.return_value = test_payload

            with patch("utils.requests.get", return_value= mock_response) as mock_get:
                 result = get_json(test_url)

                 #Ensure requests.get was called once with the correct URL
                 mock_get.assert_called_once_with(test_url)

                 #Ensure the results is the expected payload
                 self.assertEqual(result, test_payload)



if __name__ == "__main__":
    unittest.main()
