from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
    RegisterHoursWorkedResponse,
)

from .base_test_case import BaseTestCase


class RegisterHoursWorkedTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_hours_worked = self.injector.get(RegisterHoursWorked)
        self.fic_service = self.injector.get(PayoutFactorService)

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

    def test_that_request_is_granted_when_worker_is_member_of_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        amount_to_transfer = Decimal(50)
        response = self.register_hours_worked(
            RegisterHoursWorkedRequest(
                company.id, worker, hours_worked=amount_to_transfer
            )
        )
        assert not response.is_rejected

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

    @parameterized.expand(
        [
            (Decimal(10),),
            (Decimal(20),),
        ]
    )
    def test_with_no_plans_at_all_worker_receives_all_hours_worked_as_certificates(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert self.balance_checker.get_member_account_balance(worker) == hours_worked

    @parameterized.expand(
        [
            (Decimal(10),),
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
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert self.balance_checker.get_member_account_balance(worker) == hours_worked

    def test_that_with_all_public_plans_worker_receives_no_certificates(
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

    @parameterized.expand(
        [
            (Decimal(10),),
            (Decimal(20),),
        ]
    )
    def test_that_with_fic_of_one_half_worker_receives_half_of_hours_worked_as_certificates(
        self,
        hours_worked: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        # TODO: use new economic scenarios
        self._make_fic_one_half()
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert (
            self.balance_checker.get_company_account_balances(company.id).a_account
            == -hours_worked
        )
        assert (
            self.balance_checker.get_member_account_balance(worker) == hours_worked / 2
        )

    def test_that_with_negative_fic_worker_receives_negative_certificates(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker])
        self._make_fic_negative()
        hours_worked = Decimal(10)
        self.register_hours_worked(
            RegisterHoursWorkedRequest(company.id, worker, hours_worked=hours_worked)
        )
        assert self.balance_checker.get_member_account_balance(worker) < Decimal("0")

    def _make_fic_one_half(self) -> None:
        # productive plan
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        # public plan
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        assert self.fic_service.get_current_payout_factor() == Decimal("0.5")

    def _make_fic_negative(self) -> None:
        # productive plan
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        # public plan
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                labour_cost=Decimal(0), means_cost=Decimal(8), resource_cost=Decimal(0)
            ),
        )
        self.fic_service.get_current_payout_factor() < Decimal("0")


# TODO
# @injection_test
# def test_that_tax_is_four_times_hours_worked_when_fic_is_negative_three(
#     use_case: GetMemberAccount,
#     member_generator: MemberGenerator,
#     company_generator: CompanyGenerator,
#     plan_generator: PlanGenerator,
#     register_hours_worked: RegisterHoursWorked,
#     fic_service: PayoutFactorService
# ):
#     """
#     It's four times, not three times, because tax has to cover the costs of
#     the public plans AS WELL AS the work certificates
#     that have been issued to workers."""
#     hours_worked = Decimal("8.5")
#     member = member_generator.create_member()
#     company = company_generator.create_company(
#         workers=[member]
#     )
#     _make_fic_negative_three(plan_generator)
#     assert fic_service.get_current_payout_factor() == Decimal(-3)
#     register_hours_worked(
#         use_case_request=RegisterHoursWorkedRequest(
#             company_id=company,
#             worker_id=member,
#             hours_worked=hours_worked,
#         )
#     )
#     response = use_case(member)
#     transfer = response.transactions[1]
#     assert transfer.type == TransferType.taxes
#     assert transfer.transaction_volume == - (hours_worked * Decimal(4))
