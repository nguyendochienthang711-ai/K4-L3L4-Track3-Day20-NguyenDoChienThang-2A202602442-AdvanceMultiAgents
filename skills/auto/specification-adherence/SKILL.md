---
name: specification-adherence
description: WHEN implementing or modifying functions that have docstrings or when there are explicit rules for output format and behavior.
---
- Carefully read the docstring of the function you are changing and ensure your implementation matches the documented behavior, including edge cases.
- Check for any provided rules (e.g., in the task description or failed checks) and follow them exactly (e.g., money values in integer cents, specific file formats).
- Pay attention to data type conversions (e.g., strings to numbers, formatting timestamps) and handle all specified formats.
- If the function is expected to return a specific structure (like a dictionary or a CSV row), validate the output against the specification before considering the task complete.
- When in doubt, write a small verification script or test to confirm the behavior matches the specification.
