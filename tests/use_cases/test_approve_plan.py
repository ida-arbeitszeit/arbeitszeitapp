from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.records import ConsumptionType, ProductionCosts
from arbeitszeit.transactions.transaction_type import TransactionTypes
from arbeitszeit.use_cases import get_company_transactions
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
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

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ApprovePlanUseCase)
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.query_plans = self.injector.get(QueryPlans)
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumption
        )
        self.get_company_transactions_use_case = self.injector.get(
            get_company_transactions.GetCompanyTransactionsUseCase
        )

    def test_that_an_unreviewed_plan_will_be_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        approval_response = self.use_case.approve_plan(self.create_request(plan=plan))
        assert approval_response.is_plan_approved

    def test_cannot_approve_plan_that_was_already_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        request = self.create_request(plan=plan)
        self.use_case.approve_plan(request)
        approval_response = self.use_case.approve_plan(request)
        assert not approval_response.is_plan_approved

    def test_that_plan_shows_up_in_activated_plans_after_approval(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan))
        assert self.get_latest_activated_plan().plan_id == plan

    def test_that_activation_date_is_set_correctly(self) -> None:
        expected_activation_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.datetime_service.freeze_time(expected_activation_timestamp)
        plan = self.plan_generator.create_plan(approved=False)
        response = self.use_case.approve_plan(self.create_request(plan=plan))
        assert response.is_plan_approved
        assert (
            self.get_latest_activated_plan().activation_date
            == expected_activation_timestamp
        )

    def test_that_other_company_can_register_consumption_for_approved_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan))
        plan_id = self.get_latest_activated_plan().plan_id
        other_company = self.company_generator.create_company_record()
        consumption_response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                consumer=other_company.id,
                plan=plan_id,
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        self.assertFalse(consumption_response.is_rejected)

    def test_that_means_of_production_are_transfered(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(0), resource_cost=Decimal(0), means_cost=Decimal(5)
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(self.get_company_account_balances(planner).means, Decimal(5))

    def test_that_means_of_production_costs_are_correctly_rounded_and_transfered(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
                means_cost=Decimal("5.155"),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).means, Decimal("5.16")
        )

    def test_that_costs_for_resources_are_transfered(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(0), resource_cost=Decimal(5), means_cost=Decimal(0)
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).raw_material, Decimal(5)
        )

    def test_that_resource_costs_are_correctly_rounded_and_transfered(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal("5.155"),
                means_cost=Decimal(0),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).raw_material,
            Decimal("5.16"),
        )

    def test_that_labour_account_of_company_is_increased_by_planned_amount(
        self,
    ) -> None:
        expected_amount = Decimal(5)
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=expected_amount,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).work,
            expected_amount,
        )

    def test_that_product_account_is_adjusted(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(2),
                means_cost=Decimal(3),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).product,
            Decimal("-6"),
        )

    def test_that_no_transaction_for_fixed_means_is_created_when_no_fixed_means_were_planned(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(2),
                means_cost=Decimal(0),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        assert not any(
            transaction.transaction_type == TransactionTypes.credit_for_fixed_means
            for transaction in self.get_company_transactions(planner)
        )

    def test_that_no_transaction_for_liquid_means_is_created_when_no_liquid_means_were_planned(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(0),
                means_cost=Decimal(2),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan))
        assert not any(
            transaction.transaction_type == TransactionTypes.credit_for_liquid_means
            for transaction in self.get_company_transactions(planner)
        )

    def get_company_transactions(
        self, company: UUID
    ) -> List[get_company_transactions.TransactionInfo]:
        use_case_request = get_company_transactions.Request(company=company)
        response = self.get_company_transactions_use_case.get_transactions(
            request=use_case_request
        )
        return response.transactions

    def get_company_account_balances(self, company: UUID) -> AccountBalances:
        response = self.get_company_summary(company_id=company)
        assert response
        return response.account_balances

    def get_latest_activated_plan(self) -> QueriedPlan:
        response = self.query_plans(
            QueryPlansRequest(
                query_string=None,
                filter_category=PlanFilter.by_plan_id,
                sorting_category=PlanSorting.by_activation,
                include_expired_plans=False,
            )
        )
        assert response.results
        return response.results[0]

    def create_request(self, plan: UUID) -> ApprovePlanUseCase.Request:
        return ApprovePlanUseCase.Request(plan=plan)
