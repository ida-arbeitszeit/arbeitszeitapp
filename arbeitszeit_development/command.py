from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from logging import getLogger
from typing import Optional, Protocol

logger = getLogger(__name__)


class SubprocessRunner(Protocol):
    def run_command(self, command: Subprocess) -> CompletedProcess: ...


@dataclass
class Subprocess:
    command: list[str]
    capture_output: bool = False
    check: bool = True


@dataclass
class CompletedProcess:
    return_code: int
    stdout: Optional[str]
    stderr: Optional[str]


class Shell:
    def run_command(self, command: Subprocess) -> CompletedProcess:
        completed_process = subprocess.run(
            command.command,
            universal_newlines=True,
            capture_output=command.capture_output,
            check=command.check,
        )
        return CompletedProcess(
            return_code=completed_process.returncode,
            stdout=completed_process.stdout,
            stderr=completed_process.stderr,
        )


@dataclass
class LoggingSubprocessRunner:
    def __init__(self, subprocess_runner: SubprocessRunner) -> None:
        self.runner = subprocess_runner

    def run_command(self, command: Subprocess) -> CompletedProcess:
        logger.debug(
            "Run command `%s`",
            " ".join(shlex.quote(c) for c in command.command),
        )
        return self.runner.run_command(command)
