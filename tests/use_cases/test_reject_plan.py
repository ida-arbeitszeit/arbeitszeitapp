from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import ConsumptionType, ProductionCosts
from arbeitszeit.use_cases import get_company_transactions
from arbeitszeit.use_cases.get_company_summary import AccountBalances, GetCompanySummary
from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanSorting,
    QueriedPlan,
    QueryPlans,
    QueryPlansRequest,
)
from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
    RegisterProductiveConsumptionRequest,
)
from arbeitszeit.use_cases.reject_plan import RejectPlanUseCase

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RejectPlanUseCase)
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.query_plans = self.injector.get(QueryPlans)
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumption
        )
        self.get_company_transactions_use_case = self.injector.get(
            get_company_transactions.GetCompanyTransactionsUseCase
        )

    def test_that_an_unreviewed_plan_will_be_rejected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        rejection_response = self.use_case.reject_plan(self.create_request(plan=plan))
        assert rejection_response.is_rejected

    def test_cannot_rejecte_plan_that_was_already_rejected(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        request = self.create_request(plan=plan)
        self.use_case.reject_plan(request)
        rejection_response = self.use_case.reject_plan(request)
        assert not rejection_response.is_rejected

    def test_that_plan_shows_up_in_rejected_plans_after_rejection(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.reject_plan(self.create_request(plan=plan))
        assert self.get_latest_rejected_plan().plan_id == plan

    def test_that_rejection_date_is_set_correctly(self) -> None:
        expected_rejection_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.datetime_service.freeze_time(expected_rejection_timestamp)
        plan = self.plan_generator.create_plan(approved=False)
        response = self.use_case.reject_plan(self.create_request(plan=plan))
        assert response.is_rejected
        assert (
            self.get_latest_rejected_plan().rejection_date
            == expected_rejection_timestamp
        )

    def test_that_other_company_cannot_register_consumption_for_rejected_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.reject_plan(self.create_request(plan=plan))
        plan_id = self.get_latest_rejected_plan().plan_id
        other_company = self.company_generator.create_company_record()
        consumption_response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                consumer=other_company.id,
                plan=plan_id,
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        self.assertTrue(consumption_response.is_rejected)

    def test_that_company_account_balance_is_not_changed_when_plan_is_rejected(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner,
            approved=True,
            costs=ProductionCosts(
                labour_cost=Decimal(2), resource_cost=Decimal(2), means_cost=Decimal(2)
            ),
        )
        rejected_plan = self.plan_generator.create_plan(
            planner=planner,
            approved=False,
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
        response = self.get_company_summary(company_id=company)
        assert response
        return response.account_balances

    def get_latest_rejected_plan(self) -> QueriedPlan:
        response = self.query_plans(
            QueryPlansRequest(
                query_string=None,
                filter_category=PlanFilter.by_plan_id,
                sorting_category=PlanSorting.by_rejection,
            )
        )
        assert response.results
        return response.results[0]

    def create_request(self, plan: UUID) -> RejectPlanUseCase.Request:
        return RejectPlanUseCase.Request(plan=plan)
