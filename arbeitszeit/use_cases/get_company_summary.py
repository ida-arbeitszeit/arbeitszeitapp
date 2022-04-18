from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Company, Plan, SocialAccounting
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
class Expectations:
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
    expectations: Expectations
    account_balances: AccountBalances
    deviations_relative: List[Decimal]
    plan_details: List[PlanDetails]


GetCompanySummaryResponse = Optional[GetCompanySummarySuccess]


@dataclass
class GetCompanySummary:
    company_respository: CompanyRepository
    plan_repository: PlanRepository
    account_repository: AccountRepository
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.company_respository.get_by_id(company_id)
        if company is None:
            return None
        plans = self.plan_repository.get_all_plans_for_company(company.id)
        expectations = self._get_expectations(company)
        account_balances = self._get_account_balances(company)
        return GetCompanySummarySuccess(
            id=company.id,
            name=company.name,
            email=company.email,
            registered_on=company.registered_on,
            expectations=expectations,
            account_balances=account_balances,
            deviations_relative=[
                abs(account_balances.means / expectations.means) * 100
                if expectations.means
                else Decimal(0),
                abs(account_balances.raw_material / expectations.raw_material) * 100
                if expectations.raw_material
                else Decimal(0),
                abs(account_balances.work / expectations.work) * 100
                if expectations.work
                else Decimal(0),
                abs(account_balances.product / expectations.product) * 100
                if expectations.product
                else Decimal(0),
            ],
            plan_details=[self._get_plan_details(plan) for plan in plans],
        )

    def _get_plan_details(self, plan: Plan) -> PlanDetails:
        expected_sales_volume = plan.expected_sales_value
        sales_balance_of_plan = self.transaction_repository.get_sales_balance_of_plan(
            plan
        )
        sales_deviation_relative = (
            abs(sales_balance_of_plan / expected_sales_volume) * 100
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

    def _get_expectations(self, company: Company) -> Expectations:
        credits = [
            decimal_sum(
                [
                    trans.amount_received
                    for trans in self.transaction_repository.all_transactions_received_by_account(
                        account
                    )
                    if trans.sending_account == self.social_accounting.account
                ]
            )
            for account in company.accounts()[:3]
        ]
        expected_sales = decimal_sum(
            [
                trans.amount_received
                for trans in self.transaction_repository.all_transactions_received_by_account(
                    company.product_account
                )
                if trans.sending_account == self.social_accounting.account
            ]
        )
        return Expectations(
            credits[0],
            credits[1],
            credits[2],
            expected_sales,
        )

    def _get_account_balances(self, company: Company) -> AccountBalances:
        account_balances = [
            self.account_repository.get_account_balance(account)
            for account in company.accounts()
        ]
        return AccountBalances(
            account_balances[0],
            account_balances[1],
            account_balances[2],
            account_balances[3],
        )
