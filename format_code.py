#!/usr/bin/env python
"""This script applies the standard code formatting to files. For now
we only target some selected files. If you want to add a path to the
list of auto formatted files, append the path to the list with the
apropriate comment below.
"""

import subprocess
from typing import List


def main():
    format_python_files(read_autoformat_target_paths())


def read_autoformat_target_paths() -> List[str]:
    with open(".autoformattingrc") as handle:
        return [line.strip() for line in handle.read().splitlines() if line.strip()]


def format_python_files(python_files):
    subprocess.run(
        ["isort"] + python_files,
        check=True,
    )
    subprocess.run(
        ["black"] + python_files,
        check=True,
    )


if __name__ == "__main__":
    main()
