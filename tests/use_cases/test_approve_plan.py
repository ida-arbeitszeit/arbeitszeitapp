from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.entities import AccountTypes, ProductionCosts, PurposesOfPurchases
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.get_company_summary import AccountBalances, GetCompanySummary
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactions,
    TransactionInfo,
)
from arbeitszeit.use_cases.pay_means_of_production import (
    PayMeansOfProduction,
    PayMeansOfProductionRequest,
)
from arbeitszeit.use_cases.query_plans import (
    PlanFilter,
    PlanSorting,
    QueriedPlan,
    QueryPlans,
    QueryPlansRequest,
)

from .base_test_case import BaseTestCase
from .repositories import AccountRepository, PlanDraftRepository, TransactionRepository


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ApprovePlanUseCase)
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.query_plans = self.injector.get(QueryPlans)
        self.draft_repository = self.injector.get(PlanDraftRepository)
        self.pay_means_of_production = self.injector.get(PayMeansOfProduction)
        self.account_repository = self.injector.get(AccountRepository)
        self.transaction_repository = self.injector.get(TransactionRepository)
        self.get_company_transactions_use_case = self.injector.get(
            GetCompanyTransactions
        )

    def test_that_an_unreviewed_plan_will_be_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        approval_response = self.use_case.approve_plan(
            self.create_request(plan=plan.id)
        )
        assert approval_response.is_approved

    def test_cannot_approve_plan_that_was_already_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        request = self.create_request(plan=plan.id)
        self.use_case.approve_plan(request)
        approval_response = self.use_case.approve_plan(request)
        assert not approval_response.is_approved

    def test_that_plan_shows_up_in_activated_plans_after_approval(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        assert self.get_latest_activated_plan().plan_id == plan.id

    def test_that_activation_date_is_set_correctly(self) -> None:
        expected_activation_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.datetime_service.freeze_time(expected_activation_timestamp)
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        assert (
            self.get_latest_activated_plan().activation_date
            == expected_activation_timestamp
        )

    def test_that_other_company_can_pay_for_approved_plan(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        plan_id = self.get_latest_activated_plan().plan_id
        other_company = self.company_generator.create_company_entity()
        purchase_response = self.pay_means_of_production(
            PayMeansOfProductionRequest(
                buyer=other_company.id,
                plan=plan_id,
                amount=1,
                purpose=PurposesOfPurchases.means_of_prod,
            )
        )
        self.assertFalse(purchase_response.is_rejected)

    def test_that_means_of_production_are_transfered(self) -> None:
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(0), resource_cost=Decimal(0), means_cost=Decimal(5)
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).means, Decimal(5)
        )

    def test_that_means_of_production_costs_are_correctly_rounded_and_transfered(self):
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
                means_cost=Decimal("5.155"),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).means, Decimal("5.16")
        )

    def test_that_costs_for_resources_are_transfered(self) -> None:
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(0), resource_cost=Decimal(5), means_cost=Decimal(0)
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).raw_material, Decimal(5)
        )

    def test_that_resource_costs_are_correctly_rounded_and_transfered(self):
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal("5.155"),
                means_cost=Decimal(0),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).raw_material,
            Decimal("5.16"),
        )

    def test_that_no_labour_costs_are_transfered(self):
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(5),
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).work,
            Decimal(0),
        )

    def test_that_product_account_is_adjusted(self):
        plan = self.plan_generator.create_plan(
            approved=False,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(2),
                means_cost=Decimal(3),
            ),
        )
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        self.assertEqual(
            self.get_company_account_balances(plan.planner).product,
            Decimal("-6"),
        )

    def test_that_all_transactions_have_accounting_as_sender(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.use_case.approve_plan(self.create_request(plan=plan.id))
        for transaction in self.transaction_repository.get_transactions():
            account = (
                self.account_repository.get_accounts()
                .with_id(transaction.sending_account)
                .first()
            )
            assert account
            self.assertEqual(account.account_type, AccountTypes.accounting)

    def get_company_transactions(self, company: UUID) -> List[TransactionInfo]:
        response = self.get_company_transactions_use_case(company)
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
            )
        )
        assert response.results
        return response.results[0]

    def create_request(self, plan: UUID) -> ApprovePlanUseCase.Request:
        return ApprovePlanUseCase.Request(plan=plan)
