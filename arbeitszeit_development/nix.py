from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from .command import CompletedProcess, Subprocess, SubprocessRunner


@dataclass
class NixFlake:
    path: Path
    subprocess_runner: SubprocessRunner

    def shell(self, attribute: Optional[str] = None) -> NixShell:
        return NixShell(
            flake_path=self.path,
            attribute=attribute,
            subprocess_runner=self.subprocess_runner,
        )


@dataclass
class NixShell:
    flake_path: Path
    attribute: Optional[str]
    subprocess_runner: SubprocessRunner

    def run_command(self, command: Subprocess) -> CompletedProcess:
        installable = str(self.flake_path) + (
            "#" + self.attribute if self.attribute else ""
        )
        command = replace(
            command,
            command=["nix", "develop", installable, "--command"] + command.command,
        )
        return self.subprocess_runner.run_command(command)
