# Tests for PDF Downloader

This directory contains unit and integration tests for the PDF Downloader application.

## Test Structure

The tests are organized into the following categories:

1. **Utility Tests** (`tests/utils/`): Tests for utility functions and helpers
2. **Database Model Tests** (`tests/db/`): Tests for database models and operations
3. **Core Functionality Tests** (`tests/core/`): Tests for core application logic
4. **Scraper Tests** (`tests/scrapers/`): Tests for website scrapers
5. **GUI Tests** (`tests/gui/`): Tests for the PyQt GUI components

## Running Tests

### Running All Tests

To run all tests, use the `run_tests.py` script from the project root directory:

```bash
python run_tests.py
```

### Running Specific Test Categories

To run tests for a specific category, use the `--category` option:

```bash
python run_tests.py --category=utils    # Run only utility tests
python run_tests.py --category=db       # Run only database model tests
python run_tests.py --category=core     # Run only core functionality tests
python run_tests.py --category=scrapers # Run only scraper tests
python run_tests.py --category=gui      # Run only GUI tests
```

### Additional Options

- `--verbose` or `-v`: Run tests in verbose mode
- `--quiet` or `-q`: Run tests in quiet mode
- `--failfast` or `-f`: Stop on first test failure

Example:

```bash
python run_tests.py --verbose --failfast --category=core
```

## Writing New Tests

When adding new tests:

1. Follow the existing directory structure
2. Name test files with the prefix `test_`
3. Use the `unittest` framework
4. Mock external dependencies
5. Test both success and error cases

Example test file structure:

```python
import unittest
from unittest.mock import patch, MagicMock

from src.module.to_test import ClassToTest


class TestClassName(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        self.object_to_test = ClassToTest()
    
    def test_method_name(self):
        # Test a specific method
        result = self.object_to_test.method()
        self.assertEqual(result, expected_value)
    
    def test_error_condition(self):
        # Test an error condition
        with self.assertRaises(ExpectedException):
            self.object_to_test.method_that_raises()


if __name__ == "__main__":
    unittest.main()
```