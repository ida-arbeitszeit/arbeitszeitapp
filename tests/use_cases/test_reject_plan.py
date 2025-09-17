from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import ConsumptionType, ProductionCosts
from arbeitszeit.use_cases.get_company_summary import (
    AccountBalances,
    GetCompanySummaryUseCase,
)
from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumptionRequest,
    RegisterProductiveConsumptionResponse,
    RegisterProductiveConsumptionUseCase,
)
from arbeitszeit.use_cases.reject_plan import RejectPlanUseCase
from arbeitszeit.use_cases.show_my_plans import (
    PlanInfo,
    ShowMyPlansRequest,
    ShowMyPlansUseCase,
)
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RejectPlanUseCase)
        self.get_company_summary = self.injector.get(GetCompanySummaryUseCase)
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumptionUseCase
        )
        self.show_my_plans = self.injector.get(ShowMyPlansUseCase)

    def test_that_an_unreviewed_plan_will_be_rejected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False, rejected=False)
        rejection_response = self.use_case.reject_plan(self.create_request(plan=plan))
        assert rejection_response.is_plan_rejected

    def test_cannot_reject_plan_that_was_already_rejected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False, rejected=False)
        request = self.create_request(plan=plan)
        self.use_case.reject_plan(request)
        rejection_response = self.use_case.reject_plan(request)
        assert not rejection_response.is_plan_rejected

    def test_that_rejection_date_is_set_correctly(self) -> None:
        expected_rejection_timestamp = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(expected_rejection_timestamp)
        planner = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(
            planner=planner.id, approved=False, rejected=False
        )
        response = self.use_case.reject_plan(self.create_request(plan=plan))
        assert response.is_plan_rejected
        assert (
            self.get_latest_rejected_plan(planner.id).rejection_date
            == expected_rejection_timestamp
        )

    def test_that_planning_company_cannot_register_consumption_for_rejected_plan(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(
            planner=planner.id, approved=False, rejected=False
        )
        self.use_case.reject_plan(self.create_request(plan=plan))
        consumption_response = self.register_productive_consumption.execute(
            RegisterProductiveConsumptionRequest(
                consumer=planner.id,
                plan=plan,
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        assert (
            consumption_response.rejection_reason
            == RegisterProductiveConsumptionResponse.RejectionReason.plan_is_rejected
        )

    def test_that_company_account_balance_is_not_changed_when_plan_is_rejected(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner,
            approved=True,
            rejected=False,
            costs=ProductionCosts(
                labour_cost=Decimal(2), resource_cost=Decimal(2), means_cost=Decimal(2)
            ),
        )
        rejected_plan = self.plan_generator.create_plan(
            planner=planner,
            approved=False,
            rejected=False,
            costs=ProductionCosts(
                labour_cost=Decimal(5), resource_cost=Decimal(5), means_cost=Decimal(5)
            ),
        )
        self.use_case.reject_plan(self.create_request(plan=rejected_plan))
        self.assertEqual(
            self.get_company_account_balances(planner),
            AccountBalances(
                means=Decimal(2),
                raw_material=Decimal(2),
                work=Decimal(2),
                product=Decimal("-6"),
            ),
        )

    def get_company_account_balances(self, company: UUID) -> AccountBalances:
        response = self.get_company_summary.execute(company_id=company)
        assert response
        return response.account_balances

    def get_latest_rejected_plan(self, company_id: UUID) -> PlanInfo:
        response = self.show_my_plans.show_company_plans(
            request=ShowMyPlansRequest(company_id=company_id)
        )
        assert response.rejected_plans
        return response.rejected_plans[0]

    def create_request(self, plan: UUID) -> RejectPlanUseCase.Request:
        return RejectPlanUseCase.Request(plan=plan)
