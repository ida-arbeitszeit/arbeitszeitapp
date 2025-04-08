from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.psf_balance import PublicSectorFundService
from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from tests.data_generators import TransactionGenerator
from tests.use_cases.base_test_case import BaseTestCase


class PublicSectorFundServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PublicSectorFundService)
        self.transaction_generator = self.injector.get(TransactionGenerator)

    def test_balance_is_zero_if_no_plans_are_approved(self) -> None:
        psf_balance = self.service.calculate_psf_balance()
        self.assertEqual(psf_balance, 0)

    def test_that_balance_is_zero_if_there_is_a_productive_plan_approval(self) -> None:
        self.plan_generator.create_plan()
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_balance_is_negative_if_there_is_a_public_plan_approval(self) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance < Decimal(0)

    def test_that_after_registration_of_hours_worked_balance_is_zero_if_no_plan_approvals(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_after_registration_of_hours_worked_balance_is_zero_if_only_one_productive_plan_approval(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    @parameterized.expand(
        [
            (Decimal(0), Decimal(1)),
            (Decimal(0.1), Decimal(9)),
            (Decimal(0.5), Decimal(1)),
            (Decimal(0.8), Decimal(0.5)),
        ]
    )
    def test_that_balance_grows_if_payout_factor_is_smaller_than_one_and_worked_hours_are_registered(
        self, payout_factor: Decimal, hours_worked: Decimal
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(payout_factor)
        psf_balance_before = self.service.calculate_psf_balance()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after > psf_balance_before
        assert round(psf_balance_after, 4) == round(
            psf_balance_before + (hours_worked * (1 - payout_factor)), 4
        )

    @parameterized.expand(
        [
            (Decimal(10)),
            (Decimal(100)),
            (Decimal(1000)),
        ]
    )
    def test_that_balance_stays_the_same_if_payout_factor_is_one_and_worked_hours_are_registered(
        self, hours_worked: Decimal
    ) -> None:
        fic = Decimal(1)
        self.economic_scenarios.setup_environment_with_fic(fic)
        psf_balance_before = self.service.calculate_psf_balance()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after == psf_balance_before

    @parameterized.expand(
        [
            (Decimal(10), Decimal(0.95), 10, Decimal(5)),
            (Decimal(1), Decimal(1), 10, Decimal(0)),
            (Decimal(28), Decimal(0.15), 100, Decimal(2380)),
            (Decimal(28), Decimal(0.9), 100, Decimal(280)),
            (Decimal(2), Decimal(-0.5), 10, Decimal(30)),
        ]
    )
    def test_balance_equals_sum_of_tx_amounts_sent_minus_tx_amounts_received_if_no_public_plans(
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

    def test_balance_equals_sum_of_public_plans_r_plus_p_with_inverted_sign_if_no_transactions(
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
    def test_balance_equals_difference_between_sum_of_tx_amounts_sent_minus_tx_amounts_received_and_sum_of_public_plans_r_plus_p(
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

    def _register_hours_worked(
        self, company_id: UUID, worker_id: UUID, hours_worked: Decimal
    ) -> None:
        use_case = self.injector.get(RegisterHoursWorked)
        response = use_case(
            RegisterHoursWorkedRequest(company_id, worker_id, hours_worked)
        )
        assert not response.is_rejected
