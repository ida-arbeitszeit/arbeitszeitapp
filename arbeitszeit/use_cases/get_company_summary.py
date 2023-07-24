from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, Generator, Iterable, List, Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import Company, Plan, SocialAccounting, Transaction
from arbeitszeit.repositories import DatabaseGateway


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
    social_accounting: SocialAccounting
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.database_gateway.get_companies().with_id(company_id).first()
        if company is None:
            return None
        plans = (
            self.database_gateway.get_plans()
            .planned_by(company.id)
            .ordered_by_creation_date(ascending=False)
        )
        supply = self._get_suppliers_and_supply_volume(
            (transaction, company)
            for _, transaction, company in self.database_gateway.get_company_purchases()
            .where_buyer_is_company(company=company_id)
            .joined_with_transaction_and_provider()
        )
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
            plan_details=[
                self._get_plan_details(plan=plan, provided_amount=provided_amount)
                for plan, provided_amount in plans.joined_with_provided_product_amount()
            ],
            suppliers_ordered_by_volume=list(
                sorted(supply, key=lambda supplier: -supplier.volume_of_sales)
            ),
        )

    def _get_plan_details(self, plan: Plan, provided_amount: int) -> PlanDetails:
        expected_sales_volume = plan.expected_sales_value
        certificates_from_sales = (
            plan.expected_sales_value
            * Decimal(provided_amount)
            / Decimal(plan.prd_amount)
        )
        sales_balance_of_plan = certificates_from_sales - expected_sales_volume
        now = self.datetime_service.now()
        return PlanDetails(
            id=plan.id,
            name=plan.prd_name,
            is_active=plan.is_active_as_of(now),
            sales_volume=expected_sales_volume,
            sales_balance=sales_balance_of_plan,
            deviation_relative=self._calculate_deviation(
                sales_balance_of_plan, expected_sales_volume
            ),
        )

    def _get_expectations(self, company: Company) -> Expectations:
        credits = [
            decimal_sum(
                map(
                    lambda t: t.amount_received,
                    self.database_gateway.get_transactions()
                    .where_account_is_sender_or_receiver(account)
                    .where_sender_is_social_accounting(),
                )
            )
            for account in company.accounts()[:3]
        ]
        expected_sales = decimal_sum(
            map(
                lambda t: t.amount_received,
                self.database_gateway.get_transactions()
                .where_account_is_sender_or_receiver(company.product_account)
                .where_sender_is_social_accounting(),
            )
        )
        return Expectations(
            means=credits[0],
            raw_material=credits[1],
            work=credits[2],
            product=expected_sales,
        )

    def _get_account_balances(self, company: Company) -> AccountBalances:
        company_accounts = self.database_gateway.get_accounts().with_id(
            *company.accounts()
        )
        balances = dict(
            (account.id, balance)
            for account, balance in company_accounts.joined_with_balance()
        )
        return AccountBalances(
            balances[company.means_account],
            balances[company.raw_material_account],
            balances[company.work_account],
            balances[company.product_account],
        )

    def _calculate_deviation(
        self,
        account_balance: Decimal,
        expectation: Decimal,
    ) -> Decimal:
        if expectation == 0:
            if account_balance == 0:
                return Decimal(0)
            else:
                return Decimal("Infinity")
        else:
            return abs(account_balance / expectation) * 100

    def _get_suppliers_and_supply_volume(
        self, supply: Iterable[Tuple[Transaction, Company]]
    ) -> Generator[Supplier, None, None]:
        volume_by_company_id: Dict[UUID, Decimal] = defaultdict(lambda: Decimal(0))
        suppliers_by_id: Dict[UUID, Company] = dict()
        for transaction, company in supply:
            suppliers_by_id[company.id] = company
            volume_by_company_id[company.id] += transaction.amount_sent
        for company_id, volume in volume_by_company_id.items():
            yield Supplier(
                company_id=company_id,
                company_name=suppliers_by_id[company_id].name,
                volume_of_sales=volume,
            )
