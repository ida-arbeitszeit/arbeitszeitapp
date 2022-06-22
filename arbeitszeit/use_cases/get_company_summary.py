from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Dict, Iterator, List, Optional
from uuid import UUID

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Company, Plan, Purchase, SocialAccounting
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    PlanRepository,
    PurchaseRepository,
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
class Supplier:
    company_id: UUID
    company_name: str
    volume_of_sales: Decimal


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
    suppliers_ordered_by_volume: List[Supplier]


GetCompanySummaryResponse = Optional[GetCompanySummarySuccess]


@dataclass
class GetCompanySummary:
    company_respository: CompanyRepository
    plan_repository: PlanRepository
    account_repository: AccountRepository
    transaction_repository: TransactionRepository
    social_accounting: SocialAccounting
    purchase_repository: PurchaseRepository

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.company_respository.get_by_id(company_id)
        if company is None:
            return None
        plans = self.plan_repository.get_all_plans_for_company_descending(company.id)
        purchases = self.purchase_repository.get_purchases_of_company(company_id)
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
                self._calculate_deviation(
                    asdict(account_balances)[account_name],
                    asdict(expectations)[account_name],
                )
                for account_name in ["means", "raw_material", "work", "product"]
            ],
            plan_details=[self._get_plan_details(plan) for plan in plans],
            suppliers_ordered_by_volume=self._get_suppliers(purchases),
        )

    def _get_plan_details(self, plan: Plan) -> PlanDetails:
        expected_sales_volume = plan.expected_sales_value
        sales_balance_of_plan = self.transaction_repository.get_sales_balance_of_plan(
            plan
        )
        return PlanDetails(
            id=plan.id,
            name=plan.prd_name,
            is_active=plan.is_active,
            sales_volume=expected_sales_volume,
            sales_balance=sales_balance_of_plan,
            deviation_relative=self._calculate_deviation(
                sales_balance_of_plan, expected_sales_volume
            ),
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
            means=credits[0],
            raw_material=credits[1],
            work=credits[2],
            product=expected_sales,
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

    def _calculate_deviation(
        self,
        account_balance: Decimal,
        expectation: Decimal,
    ) -> Decimal:
        try:
            return abs(account_balance / expectation) * 100
        except InvalidOperation:  # zero devided by zero
            return Decimal(0)
        except DivisionByZero:  # non-zero devided by zero
            return Decimal("Infinity")

    def _get_suppliers(self, purchases: Iterator[Purchase]) -> List[Supplier]:
        suppliers_dict = self._create_dict_of_suppliers_and_volume_of_sales(purchases)
        suppliers_dict_ordered = dict(
            sorted(suppliers_dict.items(), key=lambda item: item[1], reverse=True)
        )
        suppliers_list = []
        for key, value in suppliers_dict_ordered.items():
            supplier = self.company_respository.get_by_id(key)
            assert supplier
            suppliers_list.append(
                Supplier(
                    company_id=supplier.id,
                    company_name=supplier.name,
                    volume_of_sales=value,
                )
            )
        return suppliers_list

    def _create_dict_of_suppliers_and_volume_of_sales(
        self, purchases: Iterator[Purchase]
    ) -> Dict[UUID, Decimal]:
        suppliers: Dict[UUID, Decimal] = {}
        for purchase in purchases:
            supplier_id = self.plan_repository.get_planner_id(purchase.plan)
            purchase_volume = purchase.amount * purchase.price_per_unit
            if supplier_id in suppliers:
                suppliers[supplier_id] += purchase_volume
            else:
                suppliers[supplier_id] = purchase_volume
        return suppliers
