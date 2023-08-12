from decimal import Decimal

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
    RegisterHoursWorkedResponse,
)

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)

    def test_that_request_is_rejected_if_worker_is_not_member_of_company(
        self,
    ) -> None:
        worker1 = self.member_generator.create_member()
        worker2 = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker1])
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker2, hours_worked=Decimal(50))
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
        )

    def test_that_requrest_is_granted_when_worker_is_member_of_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        amount_to_transfer = Decimal(50)
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company.id, worker, hours_worked=amount_to_transfer
            )
        )
        assert not response.is_rejected

    def test_with_no_public_plans_that_certificates_received_equal_hours_worked(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        hours_worked = Decimal(50)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert self.balance_checker.get_member_account_balance(worker) == hours_worked

    def test_that_request_with_negative_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("-1"))
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("0"))
        )
        assert response.is_rejected

    def test_that_request_with_zero_hours_worked_is_rejected_for_the_right_reason(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=Decimal("0"))
        )
        assert (
            response.rejection_reason
            == RegisterHoursWorkedResponse.RejectionReason.hours_worked_must_be_positive
        )

    def test_that_with_all_public_plans_that_worker_receives_no_certificates(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        hours_worked = Decimal(10)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert self.balance_checker.get_member_account_balance(worker) == Decimal("0")
