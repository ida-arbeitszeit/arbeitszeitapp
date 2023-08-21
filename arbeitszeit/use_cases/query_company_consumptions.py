from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator
from uuid import UUID

from arbeitszeit.records import (
    Company,
    ConsumptionType,
    Plan,
    ProductiveConsumption,
    Transaction,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ConsumptionQueryResponse:
    consumption_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    consumption_type: ConsumptionType
    price_per_unit: Decimal
    amount: int


@dataclass
class QueryCompanyConsumptions:
    database_gateway: DatabaseGateway

    def __call__(
        self,
        company: UUID,
    ) -> Iterator[ConsumptionQueryResponse]:
        consumptions = self.database_gateway.get_productive_consumptions()
        consumptions = consumptions.where_consumer_is_company(company=company)
        company_record = self.database_gateway.get_companies().with_id(company).first()
        assert company_record
        return (
            self._consumption_to_response_model(
                consumption, transaction, plan, company_record
            )
            for consumption, transaction, plan in consumptions.ordered_by_creation_date(
                ascending=False
            ).joined_with_transactions_and_plan()
        )

    def _consumption_to_response_model(
        self,
        consumption: ProductiveConsumption,
        transaction: Transaction,
        plan: Plan,
        company: Company,
    ) -> ConsumptionQueryResponse:
        if transaction.sending_account == company.raw_material_account:
            consumption_type = ConsumptionType.raw_materials
        else:
            consumption_type = ConsumptionType.means_of_prod
        return ConsumptionQueryResponse(
            consumption_date=transaction.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            consumption_type=consumption_type,
            price_per_unit=transaction.amount_sent / consumption.amount,
            amount=consumption.amount,
        )
