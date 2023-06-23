#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, Tuple


def main() -> None:
    parse_arguments()
    controller = RequirementsUpdater(
        requirements_file=RequirementsFile(
            packages=dict(),
            path=Path("constraints.txt"),
            version_string_cleaner=VersionStringCleaner(),
        ),
        python_environment=PythonEnvironment(),
        package_filter=PackageFilter(),
    )
    controller.process_requirements_file()


@dataclass
class RequirementsUpdater:
    requirements_file: RequirementsFile
    python_environment: PythonEnvironment
    package_filter: PackageFilter

    def process_requirements_file(self) -> None:
        for package in self.python_environment.get_installed_packages():
            if self.package_filter.is_package_to_be_included_in_requirements(
                package.name
            ):
                self.requirements_file.update_package(package.name, package.version)
        self.requirements_file.save_to_disk()


@dataclass
class RequirementsFile:
    packages: Dict[str, str]
    path: Path
    version_string_cleaner: VersionStringCleaner

    def save_to_disk(self) -> None:
        with open(self.path, "w") as handle:
            for name, version in self.packages_sorted_by_name():
                print(f"{name}=={version}", file=handle)

    def update_package(self, package_name: str, package_version: str) -> None:
        self.packages[package_name] = self.version_string_cleaner.clean_version_string(
            package_version
        )

    def packages_sorted_by_name(self) -> Iterable[Tuple[str, str]]:
        return sorted(
            self.packages.items(),
            key=lambda item: item[0].lower(),
        )


@dataclass
class PythonPackage:
    name: str
    version: str


class PythonEnvironment:
    def get_installed_packages(self) -> Iterator[PythonPackage]:
        process_info = subprocess.run(
            [
                "pip",
                "list",
                "--exclude-editable",
                "--format",
                "json",
            ],
            capture_output=True,
            check=True,
        )
        packages = json.loads(process_info.stdout)
        for package in packages:
            yield PythonPackage(
                name=package["name"],
                version=package["version"],
            )


class VersionStringCleaner:
    def clean_version_string(self, version_string: str) -> str:
        return (
            self._parse_three_part_version_string(version_string)
            or self._parse_two_part_version_string(version_string)
            or version_string
        )

    def _parse_three_part_version_string(self, version_string: str) -> Optional[str]:
        parts = version_string.split(".")
        try:
            major = parts[0]
            minor = parts[1]
            patch = parts[2]
        except IndexError:
            return None
        return ".".join([major, minor, patch])

    def _parse_two_part_version_string(self, version_string: str) -> Optional[str]:
        parts = version_string.split(".")
        try:
            major = parts[0]
            minor = parts[1]
        except IndexError:
            return None
        return ".".join([major, minor])


class PackageFilter:
    def is_package_to_be_included_in_requirements(self, package_name: str) -> bool:
        # Since we use a custom flask-profiler package we need to
        # exclude it from constraints.txt
        return package_name not in ["flask-profiler"]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Synchronize requirements.txt file with nix python environment.  This command must be run in a shell/process environment where the current project dependecies are installed."
    )
    parser.parse_args()


if __name__ == "__main__":
    main()