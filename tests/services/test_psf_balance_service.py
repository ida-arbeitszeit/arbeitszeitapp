from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.psf_balance import PublicSectorFundService
from arbeitszeit.records import ProductionCosts
from tests.data_generators import TransactionGenerator
from tests.use_cases.base_test_case import BaseTestCase


class PublicSectorFundServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PublicSectorFundService)
        self.transaction_generator = self.injector.get(TransactionGenerator)

    def test_psf_balance_is_zero_if_no_public_plans_and_no_transactions(self) -> None:
        psf_balance = self.service.calculate_psf_balance()
        self.assertEqual(psf_balance, 0)

    @parameterized.expand(
        [
            (Decimal(10), Decimal(0.95), 10, Decimal(5)),
            (Decimal(1), Decimal(1), 10, Decimal(0)),
            (Decimal(28), Decimal(0.15), 100, Decimal(2380)),
            (Decimal(28), Decimal(0.9), 100, Decimal(280)),
            (Decimal(2), Decimal(-0.5), 10, Decimal(30)),
        ]
    )
    def test_psf_balance_equals_sum_of_tx_amounts_sent_minus_tx_amounts_received_if_no_public_plans(
        self,
        hours_worked: Decimal,
        fic: Decimal,
        number_of_transactions: int,
        expected_psf_balance: Decimal,
    ) -> None:
        test_company_id = self.company_generator.create_company()
        test_companies = self.service.database_gateway.get_companies().with_id(
            test_company_id
        )
        assert len(test_companies) == 1
        test_company = test_companies.first()
        assert test_company and test_company.id == test_company_id
        [
            self.transaction_generator.create_transaction(
                sending_account=test_company.work_account,
                amount_received=hours_worked * fic,
                amount_sent=hours_worked,
            )
            for num in range(number_of_transactions)
        ]
        psf_balance = self.service.calculate_psf_balance()
        assert round(psf_balance, 1) == round(expected_psf_balance, 1)

    def test_psf_balance_equals_sum_of_public_plans_r_plus_p_with_inverted_sign_if_no_transactions(
        self,
    ) -> None:

        public_plan_one = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
            is_public_service=True,
        )
        public_plan_two = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(20), Decimal(20)),
            is_public_service=True,
        )
        public_plan_three = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(0), Decimal(30), Decimal(30)),
            is_public_service=True,
        )

        test_plans = (
            self.service.database_gateway.get_plans()
            .that_are_public()
            .that_are_approved()
        )
        test_plan_ids = [plan.id for plan in test_plans]
        assert test_plan_ids == [public_plan_one, public_plan_two, public_plan_three]

        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(-120)

    @parameterized.expand(
        [
            (
                Decimal(1),
                Decimal(0.5),
                ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
                120,
                Decimal(0),
            ),
            (
                Decimal(5),
                Decimal(0.2),
                ProductionCosts(Decimal(0), Decimal(20), Decimal(10)),
                50,
                Decimal(110),
            ),
            (
                Decimal(10),
                Decimal(0.8),
                ProductionCosts(Decimal(0), Decimal(10), Decimal(100)),
                200,
                Decimal(70),
            ),
            (
                Decimal(7),
                Decimal(-0.1),
                ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
                8,
                Decimal(1.6),
            ),
            (
                Decimal(13),
                Decimal(0.75),
                ProductionCosts(Decimal(0), Decimal(20), Decimal(30)),
                100,
                Decimal(175),
            ),
        ]
    )
    def test_psf_balance_equals_difference_between_sum_of_tx_amounts_sent_minus_tx_amounts_received_and_sum_of_public_plans_r_plus_p(
        self,
        hours_worked: Decimal,
        fic: Decimal,
        public_plans_production_costs: ProductionCosts,
        number_of_transactions: int,
        expected_psf_balance: Decimal,
    ) -> None:

        public_plan_one = self.plan_generator.create_plan(
            costs=public_plans_production_costs,
            is_public_service=True,
        )
        public_plan_two = self.plan_generator.create_plan(
            costs=public_plans_production_costs,
            is_public_service=True,
        )
        public_plan_three = self.plan_generator.create_plan(
            costs=public_plans_production_costs,
            is_public_service=True,
        )
        test_plans = (
            self.service.database_gateway.get_plans()
            .that_are_public()
            .that_are_approved()
        )
        test_plan_ids = [plan.id for plan in test_plans]
        assert test_plan_ids == [public_plan_one, public_plan_two, public_plan_three]

        test_company_id = self.company_generator.create_company()
        test_companies = self.service.database_gateway.get_companies().with_id(
            test_company_id
        )
        assert len(test_companies) == 1
        test_company = test_companies.first()
        assert test_company and test_company.id == test_company_id
        [
            self.transaction_generator.create_transaction(
                sending_account=test_company.work_account,
                amount_received=hours_worked * fic,
                amount_sent=hours_worked,
            )
            for num in range(number_of_transactions)
        ]

        psf_balance = self.service.calculate_psf_balance()
        assert round(psf_balance, 1) == round(expected_psf_balance, 1)
