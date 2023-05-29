from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, DivisionByZero, InvalidOperation
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import (
    Company,
    CompanyPurchase,
    Plan,
    SocialAccounting,
    Transaction,
)
from arbeitszeit.repositories import AccountRepository, DatabaseGateway


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
    account_repository: AccountRepository
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
        purchases = (
            self.database_gateway.get_company_purchases().where_buyer_is_company(
                company=company_id
            )
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
            plan_details=[self._get_plan_details(plan) for plan in plans],
            suppliers_ordered_by_volume=self._get_suppliers(
                purchases.with_transaction()
            ),
        )

    def _get_plan_details(self, plan: Plan) -> PlanDetails:
        expected_sales_volume = plan.expected_sales_value
        sales = self.database_gateway.get_transactions().that_were_a_sale_for_plan(
            plan.id
        )
        certificates_from_sales = sum(sale.amount_received for sale in sales)
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

    def _get_suppliers(
        self, purchases: Iterable[Tuple[CompanyPurchase, Transaction]]
    ) -> List[Supplier]:
        ordered_suppliers = sorted(
            self._get_suppliers_and_volume_of_sales(purchases),
            key=lambda item: item[1],
            reverse=True,
        )
        suppliers = [
            self._get_supplier_info(supplier_id, transaction_volume)
            for supplier_id, transaction_volume in ordered_suppliers
        ]
        return suppliers

    def _get_supplier_info(
        self, supplier_id: UUID, transaction_volume: Decimal
    ) -> Supplier:
        supplier = self.database_gateway.get_companies().with_id(supplier_id).first()
        assert supplier
        return Supplier(
            company_id=supplier_id,
            company_name=supplier.name,
            volume_of_sales=transaction_volume,
        )

    def _get_suppliers_and_volume_of_sales(
        self, purchases: Iterable[Tuple[CompanyPurchase, Transaction]]
    ) -> List[Tuple[UUID, Decimal]]:
        suppliers: Dict[UUID, Decimal] = defaultdict(lambda: Decimal("0"))
        for purchase, transaction in purchases:
            plan = self.database_gateway.get_plans().with_id(purchase.plan_id).first()
            assert plan
            if plan:
                suppliers[plan.planner] += transaction.amount_sent
        return list(suppliers.items())
