from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator
from uuid import UUID

from arbeitszeit.records import Plan, PrivateConsumption, Transaction
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PrivateConsumptionsQueryResponse:
    consumption_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    price_per_unit: Decimal
    amount: int
    price_total: Decimal


@dataclass
class QueryPrivateConsumptions:
    database_gateway: DatabaseGateway

    def __call__(
        self,
        member: UUID,
    ) -> Iterator[PrivateConsumptionsQueryResponse]:
        consumptions = self.database_gateway.get_private_consumptions()
        consumptions = consumptions.where_consumer_is_member(member=member)
        return (
            self._consumption_to_response_model(consumption, transaction, plan)
            for consumption, transaction, plan in consumptions.ordered_by_creation_date(
                ascending=False
            ).joined_with_transactions_and_plan()
        )

    def _consumption_to_response_model(
        self, consumption: PrivateConsumption, transaction: Transaction, plan: Plan
    ) -> PrivateConsumptionsQueryResponse:
        return PrivateConsumptionsQueryResponse(
            consumption_date=transaction.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            price_per_unit=transaction.amount_sent / consumption.amount,
            amount=consumption.amount,
            price_total=transaction.amount_sent,
        )
