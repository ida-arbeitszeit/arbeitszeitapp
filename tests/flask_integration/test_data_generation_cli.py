from uuid import uuid4

from arbeitszeit_development.dev_cli import generate
from tests.flask_integration.base_test_case import FlaskTestCase


class DataGenerationCliTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.runner = self.app.test_cli_runner()

    def test_generate_member(self) -> None:
        result = self.runner.invoke(
            generate,
            [
                "member",
                "--name",
                "Test Member",
                "--email",
                "test@example.com",
                "--password",
                "password",
            ],
        )
        assert result.exit_code == 0

    def test_generate_plan(self) -> None:
        result = self.runner.invoke(
            generate,
            [
                "plan",
                "--name",
                "Test Plan",
                "--description",
                "This is a test plan.",
                "--production-unit",
                "Test Unit",
                "--amount",
                "100",
                "--labour-cost",
                "100.00",
                "--means-cost",
                "50.00",
                "--resource-cost",
                "20.00",
                "--timeframe",
                "11",
            ],
        )
        assert result.exit_code == 0

    def test_generate_company(self) -> None:
        worker = self.member_generator.create_member()
        result = self.runner.invoke(
            generate,
            [
                "company",
                "--name",
                "Test Company",
                "--email",
                f"test{uuid4()}@example.com",
                "--password",
                "password",
                "--worker",
                str(worker),
            ],
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
        coordinator = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        result = self.runner.invoke(
            generate,
            [
                "cooperation",
                "--name",
                "Test Cooperation",
                "--coordinator",
                str(coordinator),
                "--plans",
                str(plan),
            ],
        )
        assert result.exit_code == 0

    def test_generate_worker_company_affiliation(self) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company()
        result = self.runner.invoke(
            generate,
            [
                "worker-company-affiliation",
                str(company),
                str(worker1),
                str(worker2),
            ],
        )
        assert result.exit_code == 0
