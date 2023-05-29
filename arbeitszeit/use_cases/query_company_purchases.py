from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator
from uuid import UUID

from arbeitszeit.entities import (
    Company,
    CompanyPurchase,
    Plan,
    PurposesOfPurchases,
    Transaction,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PurchaseQueryResponse:
    purchase_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    purpose: PurposesOfPurchases
    price_per_unit: Decimal
    amount: int


@dataclass
class QueryCompanyPurchases:
    database_gateway: DatabaseGateway

    def __call__(
        self,
        company: UUID,
    ) -> Iterator[PurchaseQueryResponse]:
        purchases = self.database_gateway.get_company_purchases()
        purchases = purchases.where_buyer_is_company(company=company)
        company_entity = self.database_gateway.get_companies().with_id(company).first()
        assert company_entity
        return (
            self._purchase_to_response_model(
                purchase, transaction, plan, company_entity
            )
            for purchase, transaction, plan in purchases.ordered_by_creation_date(
                ascending=False
            ).with_transaction_and_plan()
        )

    def _purchase_to_response_model(
        self,
        purchase: CompanyPurchase,
        transaction: Transaction,
        plan: Plan,
        company: Company,
    ) -> PurchaseQueryResponse:
        if transaction.sending_account == company.raw_material_account:
            purpose = PurposesOfPurchases.raw_materials
        else:
            purpose = PurposesOfPurchases.means_of_prod
        return PurchaseQueryResponse(
            purchase_date=transaction.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            purpose=purpose,
            price_per_unit=transaction.amount_sent / purchase.amount,
            amount=purchase.amount,
        )
