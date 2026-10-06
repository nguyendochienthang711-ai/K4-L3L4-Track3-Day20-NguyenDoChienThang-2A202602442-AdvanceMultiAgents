---
name: output-validation-and-regression
description: WHEN generating output files or fixing bugs to ensure correctness, run tests, and maintain project documentation.
---
- Before writing the output file, verify the exact required structure, field names, data types, and formatting (e.g., JSON vs CSV, timestamp format).
- For JSON output, ensure all values are JSON serializable (e.g., convert numpy int64 to Python int) and that the JSON is valid.
- For CSV output, adhere to the specified header order and formatting rules (e.g., quoting, timestamp format in ISO 8601 UTC).
- After making changes, run the existing test suite to ensure no regressions are introduced.
- If the task requires regression tests, create a new test file (e.g., tests/test_regressions.py) and add one test function per bug fixed, ensuring each test passes.
- Update the changelog (CHANGELOG.md) by adding a bullet for each fix under the '## Unreleased' section in the format: '- fix(<function name>): <short description>'.
