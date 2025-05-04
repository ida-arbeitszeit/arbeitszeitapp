from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Company, Plan, SocialAccounting
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType


@dataclass
class ApprovePlanUseCase:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        is_plan_approved: bool = True

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    social_accounting: SocialAccounting

    def approve_plan(self, request: Request) -> Response:
        matching_plans = self.database_gateway.get_plans().with_id(request.plan)
        plan = matching_plans.first()
        assert plan
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        if plan.is_approved:
            return self.Response(is_plan_approved=False)

        if plan.is_public_service:
            self._create_transfers_for_public_plan(planner, plan)
        else:
            self._create_transfers_for_productive_plan(planner, plan)

        return self.Response()

    def _create_transfers_for_public_plan(self, planner: Company, plan: Plan) -> None:
        # psf -> p
        transfer_of_credit_p = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=self.social_accounting.account_psf,
            credit_account=planner.means_account,
            value=plan.production_costs.means_cost,
            type=TransferType.credit_public_p,
        )
        # psf -> r
        transfer_of_credit_r = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=self.social_accounting.account_psf,
            credit_account=planner.raw_material_account,
            value=plan.production_costs.resource_cost,
            type=TransferType.credit_public_r,
        )
        # psf -> a
        transfer_of_credit_a = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=self.social_accounting.account_psf,
            credit_account=planner.work_account,
            value=plan.production_costs.labour_cost,
            type=TransferType.credit_public_a,
        )
        self.database_gateway.create_plan_approval(
            plan_id=plan.id,
            date=self.datetime_service.now(),
            transfer_of_credit_p=transfer_of_credit_p.id,
            transfer_of_credit_r=transfer_of_credit_r.id,
            transfer_of_credit_a=transfer_of_credit_a.id,
        )

    def _create_transfers_for_productive_plan(
        self, planner: Company, plan: Plan
    ) -> None:
        # prd -> p
        transfer_of_credit_p = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=planner.product_account,
            credit_account=planner.means_account,
            value=plan.production_costs.means_cost,
            type=TransferType.credit_p,
        )
        # prd -> r
        transfer_of_credit_r = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=planner.product_account,
            credit_account=planner.raw_material_account,
            value=plan.production_costs.resource_cost,
            type=TransferType.credit_r,
        )
        # prd -> a
        transfer_of_credit_a = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=planner.product_account,
            credit_account=planner.work_account,
            value=plan.production_costs.labour_cost,
            type=TransferType.credit_a,
        )
        self.database_gateway.create_plan_approval(
            plan_id=plan.id,
            date=self.datetime_service.now(),
            transfer_of_credit_p=transfer_of_credit_p.id,
            transfer_of_credit_r=transfer_of_credit_r.id,
            transfer_of_credit_a=transfer_of_credit_a.id,
        )
