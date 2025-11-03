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
    Transfer,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ConsumptionQueryResponse:
    consumption_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    consumption_type: ConsumptionType
    paid_price_per_unit: Decimal
    amount: int


@dataclass
class QueryCompanyConsumptionsInteractor:
    database_gateway: DatabaseGateway

    def execute(
        self,
        company: UUID,
    ) -> Iterator[ConsumptionQueryResponse]:
        consumptions = self.database_gateway.get_productive_consumptions()
        consumptions = consumptions.where_consumer_is_company(company=company)
        company_record = self.database_gateway.get_companies().with_id(company).first()
        assert company_record
        return (
            self._consumption_to_response_model(
                consumption, transfer, plan, company_record
            )
            for consumption, transfer, plan in consumptions.ordered_by_creation_date(
                ascending=False
            ).joined_with_transfer_and_plan()
        )

    def _consumption_to_response_model(
        self,
        consumption: ProductiveConsumption,
        transfer: Transfer,
        plan: Plan,
        company: Company,
    ) -> ConsumptionQueryResponse:
        if transfer.debit_account == company.raw_material_account:
            consumption_type = ConsumptionType.raw_materials
        else:
            consumption_type = ConsumptionType.means_of_prod
        return ConsumptionQueryResponse(
            consumption_date=transfer.date,
            plan_id=plan.id,
            product_name=plan.prd_name,
            product_description=plan.description,
            consumption_type=consumption_type,
            paid_price_per_unit=transfer.value / consumption.amount,
            amount=consumption.amount,
        )
