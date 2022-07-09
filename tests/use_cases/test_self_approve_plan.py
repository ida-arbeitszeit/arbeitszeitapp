from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import UUID

from arbeitszeit.entities import AccountTypes, ProductionCosts, PurposesOfPurchases
from arbeitszeit.use_cases import SelfApprovePlan
from arbeitszeit.use_cases.pay_means_of_production import (
    PayMeansOfProduction,
    PayMeansOfProductionRequest,
)
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector
from .repositories import (
    AccountRepository,
    PlanDraftRepository,
    PlanRepository,
    TransactionRepository,
)


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.self_approve_plan = self.injector.get(SelfApprovePlan)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.draft_repository = self.injector.get(PlanDraftRepository)
        self.plan_repository = self.injector.get(PlanRepository)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.pay_means_of_production = self.injector.get(PayMeansOfProduction)
        self.account_repository = self.injector.get(AccountRepository)
        self.transaction_repository = self.injector.get(TransactionRepository)

    def test_that_any_plan_will_be_approved(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        approval_response = self.self_approve_plan(
            self.create_request(draft_id=plan_draft.id)
        )
        assert approval_response.is_approved

    def test_plan_draft_gets_deleted_after_approval(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        response = self.self_approve_plan(self.create_request(draft_id=plan_draft.id))
        assert response.is_approved
        assert self.draft_repository.get_by_id(plan_draft.id) is None

    def test_that_true_is_returned(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        approval_response = self.self_approve_plan(
            self.create_request(draft_id=plan_draft.id)
        )
        assert approval_response.is_approved is True

    def test_that_approval_date_has_correct_day_of_month(self) -> None:
        self.datetime_service.freeze_time(datetime(year=2021, month=5, day=3))
        plan_draft = self.plan_generator.draft_plan()
        self.self_approve_plan(self.create_request(draft_id=plan_draft.id))
        new_plan = self.plan_repository.get_plan_by_id(plan_draft.id)
        assert new_plan
        assert new_plan.approval_date
        assert 3 == new_plan.approval_date.day

    def test_that_approved_plan_has_same_planner_as_draft(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        self.self_approve_plan(self.create_request(draft_id=plan_draft.id))
        new_plan = self.plan_repository.get_plan_by_id(plan_draft.id)
        assert new_plan
        assert new_plan.planner == plan_draft.planner

    def test_response_object_contains_id_of_approved_plan(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        self.assertIsNone(self.plan_repository.get_plan_by_id(plan_draft.id))
        response = self.self_approve_plan(self.create_request(draft_id=plan_draft.id))
        self.assertIsNotNone(self.plan_repository.get_plan_by_id(response.new_plan_id))

    def test_that_other_company_can_pay_for_self_approved_plan(self) -> None:
        plan_draft = self.plan_generator.draft_plan()
        response = self.self_approve_plan(self.create_request(plan_draft.id))
        other_company = self.company_generator.create_company()
        purchase_response = self.pay_means_of_production(
            PayMeansOfProductionRequest(
                buyer=other_company.id,
                plan=response.new_plan_id,
                amount=1,
                purpose=PurposesOfPurchases.means_of_prod,
            )
        )
        self.assertFalse(purchase_response.is_rejected)

    def test_that_means_of_production_are_transfered(self) -> None:
        plan = self.plan_generator.draft_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(5))
        )
        self.self_approve_plan(self.create_request(plan.id))
        self.assertEqual(
            self.account_repository.get_account_balance(plan.planner.means_account), 5
        )

    def test_that_means_of_production_costs_are_correctly_rounded_and_transfered(self):
        plan = self.plan_generator.draft_plan(
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(5.155))
        )
        self.self_approve_plan(self.create_request(plan.id))
        self.assertEqual(
            str(
                self.account_repository.get_account_balance(plan.planner.means_account)
            ),
            "5.16",
        )

    def test_that_raw_material_costs_are_transfered(self):
        plan = self.plan_generator.draft_plan(
            costs=ProductionCosts(Decimal(0), Decimal(5), Decimal(0))
        )
        self.self_approve_plan(self.create_request(plan.id))
        assert (
            self.account_repository.get_account_balance(
                plan.planner.raw_material_account
            )
            == 5
        )

    def test_that_no_labour_costs_are_transfered(self):
        plan = self.plan_generator.draft_plan(
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10))
        )
        self.self_approve_plan(self.create_request(plan.id))
        self.assertEqual(
            self.account_repository.get_account_balance(plan.planner.work_account), 0
        )

    def test_that_product_account_is_adjusted(self):
        plan = self.plan_generator.draft_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(2))
        )
        self.self_approve_plan(self.create_request(plan.id))
        self.assertEqual(
            self.account_repository.get_account_balance(plan.planner.product_account),
            -17,
        )

    def test_that_all_transactions_have_accounting_as_sender(self):
        plan = self.plan_generator.draft_plan()
        self.self_approve_plan(self.create_request(plan.id))
        for transaction in self.transaction_repository.transactions:
            self.assertEqual(
                transaction.sending_account.account_type, AccountTypes.accounting
            )

    def test_that_transactions_with_all_account_types_except_work_account_as_receivers_are_added_to_repo(
        self,
    ):
        plan = self.plan_generator.draft_plan()
        self.self_approve_plan(self.create_request(plan.id))
        added_account_types = [
            transaction.receiving_account.account_type
            for transaction in self.transaction_repository.transactions
        ]
        for expected_account_type in (
            AccountTypes.p,
            AccountTypes.r,
            AccountTypes.prd,
        ):
            self.assertIn(expected_account_type, added_account_types)
        self.assertNotIn(AccountTypes.a, added_account_types)

    def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts(self):
        plan = self.plan_generator.draft_plan()
        expected_amount_p, expected_amount_r, expected_amount_prd = (
            plan.production_costs.means_cost,
            plan.production_costs.resource_cost,
            -plan.expected_sales_value,
        )
        self.self_approve_plan(self.create_request(plan.id))

        for trans in self.transaction_repository.transactions:
            if trans.receiving_account.account_type == AccountTypes.p:
                added_amount_p = trans.amount_received
            elif trans.receiving_account.account_type == AccountTypes.r:
                added_amount_r = trans.amount_received
            elif trans.receiving_account.account_type == AccountTypes.prd:
                added_amount_prd = trans.amount_received

        self.assertEqual(expected_amount_p, added_amount_p)
        self.assertEqual(expected_amount_r, added_amount_r)
        self.assertEqual(expected_amount_prd, added_amount_prd)

    def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts_if_public_plan(
        self,
    ):
        plan = self.plan_generator.draft_plan(is_public_service=True)
        expected_amount_p, expected_amount_r, expected_amount_prd = (
            plan.production_costs.means_cost,
            plan.production_costs.resource_cost,
            0,
        )
        self.self_approve_plan(self.create_request(plan.id))

        for trans in self.transaction_repository.transactions:
            if trans.receiving_account.account_type == AccountTypes.p:
                added_amount_p = trans.amount_received
            elif trans.receiving_account.account_type == AccountTypes.r:
                added_amount_r = trans.amount_received
            elif trans.receiving_account.account_type == AccountTypes.prd:
                added_amount_prd = trans.amount_received

        self.assertEqual(expected_amount_p, added_amount_p)
        self.assertEqual(expected_amount_r, added_amount_r)
        self.assertEqual(expected_amount_prd, added_amount_prd)

    def create_request(self, draft_id: UUID) -> SelfApprovePlan.Request:
        return SelfApprovePlan.Request(draft_id=draft_id)
