import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import format_code
from arbeitszeit_development import generate_type_stubs

from . import update_bulma, update_constraints, update_python_packages
from .command import LoggingSubprocessRunner, Shell, Subprocess, SubprocessRunner
from .nix import NixFlake


def main() -> None:
    shell = LoggingSubprocessRunner(Shell())
    flake = NixFlake(path=Path(".").resolve(), subprocess_runner=shell)
    development_shell = flake.shell()
    update_flake(shell)
    update_bulma.main()
    update_python_packages.main(shell)
    update_constraints.main(development_shell)
    generate_type_stubs.main(development_shell)
    format_code.main(shell)


def update_flake(subprocess_runner: SubprocessRunner) -> None:
    subprocess_runner.run_command(
        Subprocess(command=["nix", "flake", "update"], check=True)
    )


@dataclass
class Options:
    log_level: int


def parse_arguments() -> Options:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbosity",
        "-v",
        help="Increase logging verbosity",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--quiet",
        "-q",
        help="Decrease logging verbosity",
        action="count",
        default=0,
    )
    args = parser.parse_args()
    verbosity_level = args.verbosity - args.quiet
    if verbosity_level < 0:
        log_level = logging.WARNING
    elif verbosity_level == 0:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    return Options(log_level=log_level)


if __name__ == "__main__":
    options = parse_arguments()
    logging.basicConfig(level=options.log_level)
    main()
