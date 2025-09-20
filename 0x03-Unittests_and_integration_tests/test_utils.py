#!/usr/bin/env python3
"""
Unit tests for utils.access_nested_map using parameterized inputs.
"""

import unittest
from parameterized import parameterized # type ignore
from utils import access_nested_map
from typing import Any, Dict, Tuple


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function."""

    @parameterized.expand([ #type: ignore[misc]
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any], 
        path: tuple,
        expected:object
        )-> None:
        """Test that access_nested_map returns expected results."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

        @parameterized.expand([
            ({}, ("a",)),
            ({"a": 1}, ("a", "b")),
        ])
        def test_access_nested_map_exception(
            self,
            nested_map: dict,
            path: tuple
        ) -> None:
            """ Test that access_nested_map raises KeyError with correct message."""
            with self.assertRaises(KeyError) as error:
                access_nested_map(nested_map, path)
            
            self.assertEqual(str(error.exception), repr(path[-1]))



if __name__ == "__main__":
    unittest.main()
