---
name: module-integrity-test-safety
description: WHEN working on a codebase with existing tests and module structure to prevent import errors and preserve test integrity.
---
- Do not modify any existing files in the tests/ directory; only add new test files.
- Before running tests, verify that the module under test can be imported correctly from the test location by checking the import statements and the project's structure.
- If you refactor modules, update all imports accordingly and run the existing test suite to ensure nothing is broken.
- When creating new test files, follow the project's naming conventions (e.g., test_*.py) and place them in the tests/ directory.
- Ensure that your test files have valid Python names and do not contain syntax errors that would prevent import.
