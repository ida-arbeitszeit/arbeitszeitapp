from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import Plan, PrivateConsumption, Transaction
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Consumption:
    consumption_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    price_per_unit: Decimal
    amount: int
    price_total: Decimal


@dataclass
class Response:
    consumptions: list[Consumption]


@dataclass
class Request:
    member: UUID


@dataclass
class QueryPrivateConsumptions:
    database_gateway: DatabaseGateway

    def query_private_consumptions(self, request: Request) -> Response:
        records = (
            self.database_gateway.get_private_consumptions()
            .where_consumer_is_member(member=request.member)
            .ordered_by_creation_date(ascending=False)
            .joined_with_transactions_and_plan()
        )
        consumptions = [
            self._consumption_to_response_model(consumption, transaction, plan)
            for consumption, transaction, plan in records
        ]
        return Response(consumptions=consumptions)

    def _consumption_to_response_model(
        self, consumption: PrivateConsumption, transaction: Transaction, plan: Plan
    ) -> Consumption:
        return Consumption(
            consumption_date=transaction.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            price_per_unit=transaction.amount_sent / consumption.amount,
            amount=consumption.amount,
            price_total=transaction.amount_sent,
        )
