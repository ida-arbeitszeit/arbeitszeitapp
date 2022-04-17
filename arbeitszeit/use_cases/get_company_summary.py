from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    PlanRepository,
)


@dataclass
class PlanDetails:
    id: UUID
    name: str


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
    active_plans: List[PlanDetails]


GetCompanySummaryResponse = Optional[GetCompanySummarySuccess]


@dataclass
class GetCompanySummary:
    company_respository: CompanyRepository
    plan_repository: PlanRepository
    account_repository: AccountRepository

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.company_respository.get_by_id(company_id)
        if company is None:
            return None
        plans = self.plan_repository.get_all_active_plans_for_company(company.id)
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
            active_plans=[PlanDetails(plan.id, plan.prd_name) for plan in plans],
        )
