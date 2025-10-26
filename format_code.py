#!/usr/bin/env python
"""This script applies the standard code formatting to files. For now
we only target some selected files. If you want to add a path to the
list of auto formatted files, append the path to the list with the
apropriate comment below.
"""

import os
from os import path
from typing import List

from arbeitszeit_development.command import Shell, Subprocess, SubprocessRunner


def main(subprocess_runner: SubprocessRunner):
    format_python_files(subprocess_runner, read_autoformat_target_paths())
    if is_nixfmt_installed(subprocess_runner):
        format_nix_files(subprocess_runner)


def read_autoformat_target_paths() -> List[str]:
    with open(".autoformattingrc") as handle:
        return [line.strip() for line in handle.read().splitlines() if line.strip()]


def format_python_files(
    subprocess_runner: SubprocessRunner, python_files: list[str]
) -> None:
    subprocess_runner.run_command(Subprocess(["isort"] + python_files, check=True))
    subprocess_runner.run_command(Subprocess(["black"] + python_files, check=True))


def format_nix_files(subprocess_runner: SubprocessRunner):
    for nix_file in get_nix_files():
        format_nix_file(subprocess_runner, nix_file)


def format_nix_file(subprocess_runner: SubprocessRunner, path: str):
    if (
        subprocess_runner.run_command(
            Subprocess(["nixfmt", "--check", path], capture_output=True)
        ).return_code
        != 0
    ):
        print(f"Reformatting {path}")
        subprocess_runner.run_command(Subprocess(["nixfmt", path]))


def get_nix_files():
    for root, _, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".nix"):
                yield path.join(root, file_name)


def is_nixfmt_installed(subprocess_runner: SubprocessRunner):
    try:
        subprocess_runner.run_command(
            Subprocess(["nixfmt", "--help"], capture_output=True)
        )
    except FileNotFoundError:
        return False
    return True


if __name__ == "__main__":
    main(Shell())
