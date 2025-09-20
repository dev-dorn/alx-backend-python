#!/usr/bin/env python3
"""
Unit tests for utils functions:
- access_nested_map
- get_json
- memoize
"""

import unittest
from unittest.mock import patch, Mock
from typing import Any, Dict, Tuple
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function."""

    @parameterized.expand([
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

    @parameterized.expand([
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
    """Unit tests for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict[str, Any]
    ) -> None:
        """Test that get_json returns expected payload from mocked HTTP calls."""
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        with patch("utils.requests.get", return_value=mock_response) as mock_get:
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Unit tests for the memoize decorator."""

    def test_memoize(self) -> None:
        """Test that memoize caches the result of a method call."""
        
        class TestClass:
            """Test class for memoize testing."""
            
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()
        
        # Mock the a_method to track calls
        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            test_instance = TestClass()
            
            # Call a_property twice
            result1 = test_instance.a_property()
            result2 = test_instance.a_property()
            
            # Verify correct results are returned
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            # Verify a_method was called only once due to memoization
            mock_method.assert_called_once()