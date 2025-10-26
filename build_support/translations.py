from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Protocol

from build_support import project

TRANSLATIONS_DIRECTORY = Path("arbeitszeit_flask") / "translations"
TEMPLATE_FILE = TRANSLATIONS_DIRECTORY / "messages.pot"
WIDTH = 78


def main() -> None:
    parser = _initialize_argument_parser()
    arguments = parser.parse_args()
    arguments.func(arguments)


def _initialize_argument_parser() -> argparse.ArgumentParser:
    # We associate sub-commands by setting a default "func" values
    # that is the subcommand. This way the parser will choose the
    # correct subcommand function based on the command line arguments
    # give by the user.
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(required=True)
    compile_parser = sub_parsers.add_parser("compile")
    compile_parser.set_defaults(func=compile_messages)
    update_parser = sub_parsers.add_parser("update")
    update_parser.set_defaults(func=update_catalog)
    extract_parser = sub_parsers.add_parser("extract")
    extract_parser.set_defaults(func=extract_messages)
    initialize = sub_parsers.add_parser("initialize")
    initialize.set_defaults(func=initialize_catalog)
    initialize.add_argument("locale")
    return parser


def compile_messages(arguments: object = None) -> None:
    command = [
        "python",
        "-m",
        "babel.messages.frontend",
        "compile",
        f"--directory={TRANSLATIONS_DIRECTORY}",
    ]
    subprocess.run(command, check=True, cwd=project.PATH)


def extract_messages(arguments: object = None) -> None:
    mapping_file = "build_support/babel.cfg"
    keywords = ["lazy_gettext"]
    input_paths = [
        "arbeitszeit",
        "arbeitszeit_flask",
        "arbeitszeit_web",
    ]
    command = ["python", "-m", "babel.messages.frontend", "extract"]
    for keyword in keywords:
        command.append("--keyword")
        command.append(keyword)
    command.append(f"--output-file={TEMPLATE_FILE}")
    command.append(f"--mapping-file={mapping_file}")
    for path in input_paths:
        command.append(str(path))
    subprocess.run(command, check=True, cwd=project.PATH)


def update_catalog(arguments: object = None) -> None:
    command = [
        "python",
        "-m",
        "babel.messages.frontend",
        "update",
        "--no-fuzzy-matching",
    ]
    command.append(f"--output-dir={TRANSLATIONS_DIRECTORY}")
    command.append(f"--width={WIDTH}")
    command.append(f"--input-file={TEMPLATE_FILE}")
    subprocess.run(command, check=True, cwd=project.PATH)


def initialize_catalog(arguments: InitializeArguments) -> None:
    command = ["python", "-m", "babel.messages.frontend", "init"]
    command.append(f"--input-file={TEMPLATE_FILE}")
    command.append(f"--output-dir={TRANSLATIONS_DIRECTORY}")
    command.append(f"--locale={arguments.locale}")
    command.append(f"--width={WIDTH}")
    subprocess.run(command, check=True, cwd=project.PATH)


class InitializeArguments(Protocol):
    @property
    def locale(self) -> str: ...


if __name__ == "__main__":
    main()
