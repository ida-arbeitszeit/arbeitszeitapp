from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    PlanRepository,
    TransactionRepository,
)


@dataclass
class PlanDetails:
    id: UUID
    name: str
    is_active: bool
    sales_volume: Decimal
    sales_balance: Decimal
    deviation_relative: Decimal


@dataclass
class AccountBalances:
    means: Decimal
    raw_material: Decimal
    work: Decimal
    product: Decimal


@dataclass
class GetCompanySummarySuccess:
    id: UUID
    name: str
    email: str
    registered_on: datetime
    account_balances: AccountBalances
    plan_details: List[PlanDetails]


GetCompanySummaryResponse = Optional[GetCompanySummarySuccess]


@dataclass
class GetCompanySummary:
    company_respository: CompanyRepository
    plan_repository: PlanRepository
    account_repository: AccountRepository
    transaction_repository: TransactionRepository

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.company_respository.get_by_id(company_id)
        if company is None:
            return None
        plans = self.plan_repository.get_all_plans_for_company(company.id)
        return GetCompanySummarySuccess(
            id=company.id,
            name=company.name,
            email=company.email,
            registered_on=company.registered_on,
            account_balances=AccountBalances(
                self.account_repository.get_account_balance(company.means_account),
                self.account_repository.get_account_balance(
                    company.raw_material_account
                ),
                self.account_repository.get_account_balance(company.work_account),
                self.account_repository.get_account_balance(company.product_account),
            ),
            plan_details=[self._get_plan_details(plan) for plan in plans],
        )

    def _get_plan_details(self, plan: Plan) -> PlanDetails:
        expected_sales_volume = plan.expected_sales_value
        sales_balance_of_plan = self.transaction_repository.get_sales_balance_of_plan(
            plan
        )
        sales_deviation_relative = (
            (sales_balance_of_plan / expected_sales_volume) * 100
            if expected_sales_volume
            else Decimal(0)
        )
        return PlanDetails(
            id=plan.id,
            name=plan.prd_name,
            is_active=plan.is_active,
            sales_volume=expected_sales_volume,
            sales_balance=sales_balance_of_plan,
            deviation_relative=sales_deviation_relative,
        )
