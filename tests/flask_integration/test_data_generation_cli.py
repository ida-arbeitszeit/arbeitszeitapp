from tests.flask_integration.dev_cli import generate
from tests.flask_integration.flask import FlaskTestCase


class DataGenerationCliTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.runner = self.app.test_cli_runner()

    def test_generate_plan(self) -> None:
        result = self.runner.invoke(
            generate,
            ["plan", "--labour-cost", "100.00"],
        )
        assert result.exit_code == 0

    def test_generate_company(self) -> None:
        result = self.runner.invoke(
            generate,
            ["company"],
        )
        assert result.exit_code == 0

    def test_generate_private_consumption(self) -> None:
        result = self.runner.invoke(
            generate,
            ["private-consumption"],
        )
        assert result.exit_code == 0

    def test_generate_productive_consumption_of_r(self) -> None:
        result = self.runner.invoke(
            generate,
            ["productive-consumption-of-r"],
        )
        assert result.exit_code == 0

    def test_generate_productive_consumption_of_p(self) -> None:
        result = self.runner.invoke(
            generate,
            ["productive-consumption-of-p"],
        )
        assert result.exit_code == 0

    def test_generate_cooperation(self) -> None:
        result = self.runner.invoke(
            generate,
            ["cooperation"],
        )
        assert result.exit_code == 0
