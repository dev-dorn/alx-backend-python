# 0x03. Unittests and Integration Tests

This project contains unit tests and integration tests written in Python 3.7.  
The goal is to practice test-driven development (TDD), parameterized testing, mocking, and integration testing techniques.  

All code and tests follow the ALX requirements:
- All files are interpreted/compiled on **Ubuntu 18.04 LTS using Python 3.7**.
- All Python files start with `#!/usr/bin/env python3`.
- All files end with a new line.
- All files are **pycodestyle (version 2.5)** compliant.
- All files are executable.
- Each module, class, and function contains a **full documentation string** (docstring).
- All functions and coroutines use **type annotations**.

---

---

## Task 1: Parameterize a unit test
We implemented parameterized unit tests for the function `utils.access_nested_map`.  
This function retrieves a value from a nested dictionary using a given tuple path.  

### Example Behavior
```python
>>> access_nested_map({"a": 1}, ("a",))
1
>>> access_nested_map({"a": {"b": 2}}, ("a",))
{"b": 2}
>>> access_nested_map({"a": {"b": 2}}, ("a", "b"))
2



