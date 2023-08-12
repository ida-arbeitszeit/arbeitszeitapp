from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator
from uuid import UUID

from arbeitszeit.records import ConsumerPurchase, Plan, Transaction
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PurchaseQueryResponse:
    purchase_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    price_per_unit: Decimal
    amount: int
    price_total: Decimal


@dataclass
class QueryMemberPurchases:
    database_gateway: DatabaseGateway

    def __call__(
        self,
        member: UUID,
    ) -> Iterator[PurchaseQueryResponse]:
        purchases = self.database_gateway.get_consumer_purchases()
        purchases = purchases.where_buyer_is_member(member=member)
        return (
            self._purchase_to_response_model(purchase, transaction, plan)
            for purchase, transaction, plan in purchases.ordered_by_creation_date(
                ascending=False
            ).joined_with_transactions_and_plan()
        )

    def _purchase_to_response_model(
        self, purchase: ConsumerPurchase, transaction: Transaction, plan: Plan
    ) -> PurchaseQueryResponse:
        return PurchaseQueryResponse(
            purchase_date=transaction.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            price_per_unit=transaction.amount_sent / purchase.amount,
            amount=purchase.amount,
            price_total=transaction.amount_sent,
        )
