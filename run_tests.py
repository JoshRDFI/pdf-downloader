#!/usr/bin/env python3

"""
Test runner for the PDF Downloader application.

This script runs all the tests in the project in a logical order:
1. Utility tests
2. Database model tests
3. Core functionality tests
4. Scraper tests
5. GUI tests

Usage:
    python run_tests.py [options]

Options:
    --verbose, -v: Run tests in verbose mode
    --quiet, -q: Run tests in quiet mode
    --failfast, -f: Stop on first test failure
    --category=CATEGORY: Run only tests in the specified category
                        (utils, db, core, scrapers, gui, or all)
"""

import unittest
import sys
import os


def discover_tests(start_dir, pattern='test_*.py'):
    """Discover tests in the specified directory."""
    return unittest.defaultTestLoader.discover(start_dir, pattern=pattern)


def run_tests(test_suite, verbosity=1, failfast=False):
    """Run the specified test suite."""
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    return runner.run(test_suite)


def main():
    """Main function to run all tests."""
    # Parse command line arguments
    verbosity = 1
    failfast = False
    category = 'all'
    
    for arg in sys.argv[1:]:
        if arg in ('--verbose', '-v'):
            verbosity = 2
        elif arg in ('--quiet', '-q'):
            verbosity = 0
        elif arg in ('--failfast', '-f'):
            failfast = True
        elif arg.startswith('--category='):
            category = arg.split('=')[1].lower()
    
    # Ensure we're in the project root directory
    if not os.path.exists('src') or not os.path.exists('tests'):
        print("Error: This script must be run from the project root directory.")
        sys.exit(1)
    
    # Create test suites for each category
    test_suites = {}
    
    # 1. Utility tests
    if category in ('utils', 'all'):
        print("\n=== Running Utility Tests ===")
        test_suites['utils'] = discover_tests('tests/utils')
        result_utils = run_tests(test_suites['utils'], verbosity, failfast)
        if not result_utils.wasSuccessful() and failfast:
            return 1
    
    # 2. Database model tests
    if category in ('db', 'all'):
        print("\n=== Running Database Model Tests ===")
        test_suites['db'] = discover_tests('tests/db')
        result_db = run_tests(test_suites['db'], verbosity, failfast)
        if not result_db.wasSuccessful() and failfast:
            return 1
    
    # 3. Core functionality tests
    if category in ('core', 'all'):
        print("\n=== Running Core Functionality Tests ===")
        test_suites['core'] = discover_tests('tests/core')
        result_core = run_tests(test_suites['core'], verbosity, failfast)
        if not result_core.wasSuccessful() and failfast:
            return 1
    
    # 4. Scraper tests
    if category in ('scrapers', 'all'):
        print("\n=== Running Scraper Tests ===")
        test_suites['scrapers'] = discover_tests('tests/scrapers')
        result_scrapers = run_tests(test_suites['scrapers'], verbosity, failfast)
        if not result_scrapers.wasSuccessful() and failfast:
            return 1
    
    # 5. GUI tests
    if category in ('gui', 'all'):
        print("\n=== Running GUI Tests ===")
        test_suites['gui'] = discover_tests('tests/gui')
        result_gui = run_tests(test_suites['gui'], verbosity, failfast)
        if not result_gui.wasSuccessful() and failfast:
            return 1
    
    # Run all tests together if requested
    if category == 'all':
        print("\n=== Summary ===")
        all_tests = unittest.TestSuite()
        for suite in test_suites.values():
            all_tests.addTest(suite)
        
        total_tests = all_tests.countTestCases()
        print(f"Total tests: {total_tests}")
        
        # Count passed and failed tests
        passed = 0
        failed = 0
        errors = 0
        
        for suite_name, suite in test_suites.items():
            suite_result = unittest.TestResult()
            suite.run(suite_result)
            passed += suite_result.testsRun - len(suite_result.failures) - len(suite_result.errors)
            failed += len(suite_result.failures)
            errors += len(suite_result.errors)
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        
        success = (failed == 0 and errors == 0)
        print(f"Overall result: {'SUCCESS' if success else 'FAILURE'}")
        
        return 0 if success else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())