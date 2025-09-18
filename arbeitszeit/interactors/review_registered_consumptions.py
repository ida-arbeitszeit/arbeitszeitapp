from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RegisteredConsumption:
    date: datetime
    is_private_consumption: bool
    consumer_name: str
    consumer_id: UUID
    product_name: str
    plan_id: UUID
    labour_hours_consumed: Decimal


@dataclass
class ReviewRegisteredConsumptionsInteractor:
    @dataclass
    class Request:
        providing_company: UUID

    @dataclass
    class Response:
        consumptions: list[RegisteredConsumption]

    database: DatabaseGateway

    def review_registered_consumptions(self, request: Request) -> Response:
        private_consumptions = self._get_private_consumptions(request)
        productive_consumptions = self._get_productive_consumptions(request)
        consumptions = private_consumptions + productive_consumptions
        consumptions_ordered_by_date_in_descending_order = sorted(
            consumptions, key=lambda consumption: consumption.date, reverse=True
        )
        return self.Response(
            consumptions=consumptions_ordered_by_date_in_descending_order
        )

    def _get_private_consumptions(
        self, request: Request
    ) -> list[RegisteredConsumption]:
        return [
            RegisteredConsumption(
                date=transfer.date,
                is_private_consumption=True,
                consumer_name=member.name,
                consumer_id=member.id,
                product_name=plan.prd_name,
                plan_id=plan.id,
                labour_hours_consumed=transfer.value,
            )
            for _, transfer, plan, member in self.database.get_private_consumptions()
            .where_provider_is_company(request.providing_company)
            .joined_with_transfer_and_plan_and_consumer()
        ]

    def _get_productive_consumptions(
        self, request: Request
    ) -> list[RegisteredConsumption]:
        productive_consumptions: list[RegisteredConsumption] = []
        productive_consumptions_result = (
            self.database.get_productive_consumptions()
            .where_provider_is_company(request.providing_company)
            .joined_with_transfer_and_plan_and_consumer()
        )
        for _, transfer, plan, company in productive_consumptions_result:
            productive_consumptions.append(
                RegisteredConsumption(
                    date=transfer.date,
                    is_private_consumption=False,
                    consumer_name=company.name,
                    consumer_id=company.id,
                    product_name=plan.prd_name,
                    plan_id=plan.id,
                    labour_hours_consumed=transfer.value,
                )
            )
        return productive_consumptions
