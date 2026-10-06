"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use to explore the workspace, read files (README, docstrings, data schemas, log samples), "
                "inspect directory structure, and report factual findings without modifying any files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Inspect the workspace, read instructions, docstrings, schemas, "
                "and sample files. Report your factual findings clearly and concisely. Do NOT modify any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to perform code or data modifications, execute commands, run tests and scripts, "
                "and report execution results and changed files."
            ),
            "system_prompt": (
                "You are an implementation subagent. Perform the requested modifications, run tests and scripts "
                "using the shell to verify your work, and report exactly what files you changed and whether tests passed."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use to independently review modified files, verify edge cases and rule compliance against task "
                "instructions, and report any discrepancies without modifying files."
            ),
            "system_prompt": (
                "You are a review subagent. Independently inspect the files and outputs against all task requirements, "
                "edge cases, and rules. Report any issues or confirm correctness. Do NOT modify any files."
            ),
        },
    ]

