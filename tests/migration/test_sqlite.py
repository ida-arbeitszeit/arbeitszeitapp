import os
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase

from . import sqlite_test_settings


class SqliteMigrationTests(TestCase):
    def setUp(self) -> None:
        self.environment_variables = dict(os.environ)
        self.environment_variables[
            "ARBEITSZEITAPP_CONFIGURATION_PATH"
        ] = sqlite_test_settings.__file__
        self.environment_variables["PYTHONPATH"] = ":".join(sys.path)
        self.environment_variables["FLASK_APP"] = "arbeitszeit_flask"

    def test_forward_migrations_work(self) -> None:
        with TemporaryDirectory() as cwd:
            self.environment_variables[
                "ARBEITSZEITAPP_TEST_DB_URL"
            ] = f"sqlite:///{cwd}/test.db"
            completed_process = subprocess.run(
                ["flask", "db", "upgrade"],
                env=self.environment_variables,
                capture_output=True,
                universal_newlines=True,
                cwd=cwd,
            )
            assert completed_process.returncode == 0, completed_process.stderr

    def test_backwards_migrations_work(self) -> None:
        with TemporaryDirectory() as cwd:
            self.environment_variables[
                "ARBEITSZEITAPP_TEST_DB_URL"
            ] = f"sqlite:///{cwd}/test.db"
            subprocess.run(
                ["flask", "db", "upgrade"],
                env=self.environment_variables,
                capture_output=True,
                universal_newlines=True,
                cwd=cwd,
            )
            completed_process = subprocess.run(
                ["flask", "db", "downgrade", "5ccb2cf7d04c"],
                env=self.environment_variables,
                capture_output=True,
                universal_newlines=True,
                cwd=cwd,
            )
            assert completed_process.returncode == 0, completed_process.stderr
