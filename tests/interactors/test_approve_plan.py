from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.interactors.approve_plan import ApprovePlanInteractor
from arbeitszeit.interactors.get_company_summary import (
    AccountBalances,
    GetCompanySummaryInteractor,
)
from arbeitszeit.interactors.query_plans import (
    PlanFilter,
    PlanSorting,
    QueriedPlan,
    QueryPlansInteractor,
    QueryPlansRequest,
)
from arbeitszeit.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionInteractor,
    RegisterProductiveConsumptionRequest,
)
from arbeitszeit.records import ConsumptionType, ProductionCosts, SocialAccounting
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ApprovePlanInteractor)
        self.get_company_summary = self.injector.get(GetCompanySummaryInteractor)
        self.query_plans_interactor = self.injector.get(QueryPlansInteractor)
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumptionInteractor
        )

    def test_that_an_unreviewed_plan_will_be_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        approval_response = self.interactor.approve_plan(self.create_request(plan=plan))
        assert approval_response.is_plan_approved

    def test_cannot_approve_plan_that_was_already_approved(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        request = self.create_request(plan=plan)
        self.interactor.approve_plan(request)
        approval_response = self.interactor.approve_plan(request)
        assert not approval_response.is_plan_approved

    def test_that_plan_shows_up_in_activated_plans_after_approval(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.interactor.approve_plan(self.create_request(plan=plan))
        assert self.get_latest_activated_plan().plan_id == plan

    def test_that_approval_date_is_set_correctly(self) -> None:
        expected_approval_timestamp = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(expected_approval_timestamp)
        plan = self.plan_generator.create_plan(approved=False)
        response = self.interactor.approve_plan(self.create_request(plan=plan))
        assert response.is_plan_approved
        assert (
            self.get_latest_activated_plan().approval_date
            == expected_approval_timestamp
        )

    def test_that_other_company_can_register_consumption_for_approved_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.interactor.approve_plan(self.create_request(plan=plan))
        plan_id = self.get_latest_activated_plan().plan_id
        other_company = self.company_generator.create_company_record()
        consumption_response = self.register_productive_consumption.execute(
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
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.assertEqual(self.get_company_account_balances(planner).means, Decimal(5))

    def test_that_costs_for_resources_are_transfered(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(0), resource_cost=Decimal(5), means_cost=Decimal(0)
            ),
        )
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).raw_material, Decimal(5)
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
        self.interactor.approve_plan(self.create_request(plan=plan))
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
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.assertEqual(
            self.get_company_account_balances(planner).product,
            Decimal("-6"),
        )

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_three_transfers_are_created_on_approval(
        self,
        is_public_service: bool,
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=False,
            is_public_service=is_public_service,
        )
        self.interactor.approve_plan(self.create_request(plan=plan))
        assert len(list(self.database_gateway.get_transfers())) == 3

    @parameterized.expand(
        [
            (Decimal(0), True),
            (Decimal(1), True),
            (Decimal(2.50001), True),
            (Decimal(0), False),
            (Decimal(1), False),
            (Decimal(2.50001), False),
        ]
    )
    def test_that_one_transfer_of_credit_p_is_created_on_plan_approval(
        self,
        planned_p_amount: Decimal,
        is_public_service: bool,
    ) -> None:
        planner = self.company_generator.create_company_record()
        debit_account = (
            self.injector.get(SocialAccounting).account_psf
            if is_public_service
            else planner.product_account
        )
        expected_transfer_type = (
            TransferType.credit_public_p if is_public_service else TransferType.credit_p
        )
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner.id,
            is_public_service=is_public_service,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(1),
                means_cost=planned_p_amount,
            ),
        )
        approval_time = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(approval_time)
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.datetime_service.unfreeze_time()
        transfers = list(self.database_gateway.get_transfers())
        transfers_of_credit_p = list(
            filter(lambda transfer: transfer.type == expected_transfer_type, transfers)
        )
        assert len(transfers_of_credit_p) == 1
        transfer = transfers_of_credit_p[0]
        assert transfer.debit_account == debit_account
        assert transfer.credit_account == planner.means_account
        assert transfer.value == planned_p_amount
        assert transfer.type == expected_transfer_type
        assert transfer.date == approval_time

    @parameterized.expand(
        [
            (Decimal(0), True),
            (Decimal(1), True),
            (Decimal(2.50001), True),
            (Decimal(0), False),
            (Decimal(1), False),
            (Decimal(2.50001), False),
        ]
    )
    def test_that_one_transfer_of_credit_r_is_created_on_plan_approval(
        self,
        planned_r_amount: Decimal,
        is_public_service: bool,
    ) -> None:
        planner = self.company_generator.create_company_record()
        debit_account = (
            self.injector.get(SocialAccounting).account_psf
            if is_public_service
            else planner.product_account
        )
        expected_transfer_type = (
            TransferType.credit_public_r if is_public_service else TransferType.credit_r
        )
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner.id,
            is_public_service=is_public_service,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=planned_r_amount,
                means_cost=Decimal(1),
            ),
        )
        approval_time = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(approval_time)
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.datetime_service.unfreeze_time()
        transfers = list(self.database_gateway.get_transfers())
        transfers_of_credit_r = list(
            filter(lambda transfer: transfer.type == expected_transfer_type, transfers)
        )
        assert len(transfers_of_credit_r) == 1
        transfer = transfers_of_credit_r[0]
        assert transfer.debit_account == debit_account
        assert transfer.credit_account == planner.raw_material_account
        assert transfer.value == planned_r_amount
        assert transfer.type == expected_transfer_type
        assert transfer.date == approval_time

    @parameterized.expand(
        [
            (Decimal(0), True),
            (Decimal(1), True),
            (Decimal(2.50001), True),
            (Decimal(0), False),
            (Decimal(1), False),
            (Decimal(2.50001), False),
        ]
    )
    def test_that_one_transfer_of_credit_a_is_created_on_plan_approval(
        self,
        planned_a_amount: Decimal,
        is_public_service: bool,
    ) -> None:
        planner = self.company_generator.create_company_record()
        debit_account = (
            self.injector.get(SocialAccounting).account_psf
            if is_public_service
            else planner.product_account
        )
        expected_transfer_type = (
            TransferType.credit_public_a if is_public_service else TransferType.credit_a
        )
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=planner.id,
            is_public_service=is_public_service,
            costs=ProductionCosts(
                labour_cost=planned_a_amount,
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
        )
        approval_time = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(approval_time)
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.datetime_service.unfreeze_time()
        transfers = list(self.database_gateway.get_transfers())
        transfers_of_credit_a = list(
            filter(lambda transfer: transfer.type == expected_transfer_type, transfers)
        )
        assert len(transfers_of_credit_a) == 1
        transfer = transfers_of_credit_a[0]
        assert transfer.debit_account == debit_account
        assert transfer.credit_account == planner.work_account
        assert transfer.value == planned_a_amount
        assert transfer.type == expected_transfer_type
        assert transfer.date == approval_time

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_one_plan_approval_record_is_created(
        self,
        is_public_service: bool,
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=False,
            is_public_service=is_public_service,
        )
        approval_time = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(approval_time)
        self.interactor.approve_plan(self.create_request(plan=plan))
        self.datetime_service.unfreeze_time()
        assert len(list(self.database_gateway.get_plan_approvals())) == 1
        plan_approval = list(self.database_gateway.get_plan_approvals())[0]
        assert plan_approval.plan_id == plan
        assert plan_approval.date == approval_time

    def get_company_account_balances(self, company: UUID) -> AccountBalances:
        response = self.get_company_summary.execute(company_id=company)
        assert response
        return response.account_balances

    def get_latest_activated_plan(self) -> QueriedPlan:
        response = self.query_plans_interactor.execute(
            QueryPlansRequest(
                query_string=None,
                filter_category=PlanFilter.by_plan_id,
                sorting_category=PlanSorting.by_activation,
                include_expired_plans=False,
            )
        )
        assert response.results
        return response.results[0]

    def create_request(self, plan: UUID) -> ApprovePlanInteractor.Request:
        return ApprovePlanInteractor.Request(plan=plan)
