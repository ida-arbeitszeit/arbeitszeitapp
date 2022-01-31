#!/usr/bin/env python
"""This script applies the standard code formatting to files. For now
we only target some selected files. If you want to add a path to the
list of auto formatted files, append the path to the list with the
apropriate comment below.
"""

import os
import subprocess
from os import path
from typing import List


def main():
    format_python_files(read_autoformat_target_paths())
    format_nix_files()


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


def format_nix_files():
    for nix_file in get_nix_files():
        format_nix_file(nix_file)


def format_nix_file(path):
    if subprocess.run(["nixfmt", "--check", path], capture_output=True).returncode != 0:
        print(f"Reformatting {path}")
        subprocess.run(["nixfmt", path])


def get_nix_files():
    for root, _, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".nix"):
                yield path.join(root, file_name)


if __name__ == "__main__":
    main()
