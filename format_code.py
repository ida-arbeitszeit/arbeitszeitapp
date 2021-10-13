#!/usr/bin/env python
"""This script applies the standard code formatting to files. For now
we only target some selected files. If you want to add a path to the
list of auto formatted files, append the path to the list with the
apropriate comment below.
"""

import subprocess


def main():
    format_python_files(
        # Add your path here if you want to apply autoformatting to it
        [
            "arbeitszeit/",
            "arbeitszeit_web/",
            "tests/",
            "project/",
            "format_code.py",
            "type_stubs",
        ]
    )


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
