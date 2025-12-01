from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.interactors.register_hours_worked import (
    RegisterHoursWorkedInteractor,
    RegisterHoursWorkedRequest,
    RegisterHoursWorkedResponse,
)
from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.payout_factor import PayoutFactorService

from .base_test_case import BaseTestCase


class RegisterHoursWorkedTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_hours_worked = self.injector.get(RegisterHoursWorkedInteractor)
        self.fic_service = self.injector.get(PayoutFactorService)

    def test_that_request_is_rejected_if_worker_is_not_member_of_company(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker1])
        response = self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker2, hours_worked=Decimal(50))
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
        )
        assert not response.registered_hours_worked_id

    def test_that_request_is_granted_when_worker_is_member_of_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        amount_to_transfer = Decimal(50)
        response = self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(
                company.id, worker, hours_worked=amount_to_transfer
            )
        )
        assert not response.is_rejected
        assert response.registered_hours_worked_id

    def test_that_request_with_negative_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("-1"))
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("0"))
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected_for_the_right_reason(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("0"))
        )
        assert (
            response.rejection_reason
            == RegisterHoursWorkedResponse.RejectionReason.hours_worked_must_be_positive
        )
        assert not response.registered_hours_worked_id

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_with_no_plans_at_all_worker_receives_all_hours_worked_as_certificates(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        self.assertAlmostEqual(
            self.balance_checker.get_member_account_balance(worker), hours_worked
        )

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_with_no_plans_at_all_company_gets_deducted_all_hours_worked(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_that_with_all_productive_plans_worker_receives_all_hours_worked_as_certificates(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(10),
                resource_cost=Decimal(10),
            ),
        )
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        self.assertAlmostEqual(
            self.balance_checker.get_member_account_balance(worker), hours_worked
        )

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_that_with_all_productive_plans_company_gets_deducted_all_hours_worked(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(10),
                resource_cost=Decimal(10),
            ),
        )
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_that_with_fic_of_one_half_worker_receives_half_of_hours_worked_as_certificates(
        self,
        hours_worked: Decimal,
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(Decimal(0.5))
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        self.assertAlmostEqual(
            self.balance_checker.get_member_account_balance(worker), hours_worked / 2
        )

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_that_with_fic_of_one_half_company_gets_deducted_half_of_hours_worked(
        self,
        hours_worked: Decimal,
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(Decimal(0.5))
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )

    def test_that_with_fic_of_zero_worker_receives_zero_certificates(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self._make_fic_zero()
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal(10))
        )
        assert self.balance_checker.get_member_account_balance(worker) == Decimal("0")

    @parameterized.expand(
        [
            (Decimal(5.3),),
            (Decimal(20),),
        ]
    )
    def test_that_with_fic_of_zero_company_gets_deducted_all_hours_worked(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self._make_fic_zero()
        self.register_hours_worked.execute(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )

    def _make_fic_zero(self) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(10),
                resource_cost=Decimal(10),
            ),
        )
        assert self.fic_service.calculate_current_payout_factor() == Decimal("0")
