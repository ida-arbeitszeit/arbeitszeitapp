from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class CompensationTransferService:
    """
    For background on compensation transfers see project's developer documentation.
    """

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def create_compensation_transfer(
        self,
        coop_price_per_unit: Decimal,
        plan_price_per_unit: Decimal,
        consumed_amount: int,
        planner_product_account: UUID,
        cooperation_account: UUID,
    ) -> UUID | None:
        difference = coop_price_per_unit - plan_price_per_unit
        if not difference:
            return None
        elif difference < Decimal(0):
            """Plan is underproductive."""
            return self._compensate_company(
                consumed_amount=consumed_amount,
                difference=abs(difference),
                cooperation_account=cooperation_account,
                planner_product_account=planner_product_account,
            )
        else:
            """Plan is overproductive."""
            return self._compensate_cooperation(
                consumed_amount=consumed_amount,
                difference=abs(difference),
                cooperation_account=cooperation_account,
                planner_product_account=planner_product_account,
            )

    def _compensate_cooperation(
        self,
        consumed_amount: int,
        difference: Decimal,
        cooperation_account: UUID,
        planner_product_account: UUID,
    ) -> UUID:
        transfer = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=planner_product_account,
            credit_account=cooperation_account,
            value=difference * consumed_amount,
            type=TransferType.compensation_for_coop,
        )
        return transfer.id

    def _compensate_company(
        self,
        consumed_amount: int,
        difference: Decimal,
        cooperation_account: UUID,
        planner_product_account: UUID,
    ) -> UUID:
        transfer = self.database_gateway.create_transfer(
            date=self.datetime_service.now(),
            debit_account=cooperation_account,
            credit_account=planner_product_account,
            value=difference * consumed_amount,
            type=TransferType.compensation_for_company,
        )
        return transfer.id
