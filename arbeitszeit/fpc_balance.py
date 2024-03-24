from dataclasses import dataclass
# from datetime import datetime
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PublicFundService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    # def calculate_payout_factor(self, timestamp: datetime) -> Decimal:
    #     active_plans = (
    #         self.database_gateway.get_plans()
    #         .that_will_expire_after(timestamp)
    #         .that_were_activated_before(timestamp)
    #     )
    #     return calculate_payout_factor(active_plans)

    def get_current_fpc_balance(self) -> Decimal:
        # now = self.datetime_service.now()
        # TODO fetch this from database_gateway
        return Decimal(0)
