from dataclasses import dataclass

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.payout_factor import PayoutFactorService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CalculateFicAndUpdateExpiredPlans:
    datetime_service: DatetimeService
    payout_factor_service: PayoutFactorService
    database_gateway: DatabaseGateway

    def __call__(self) -> None:
        """This function should be called at least once per day,
        preferably more often (e.g. every hour).
        """
        now = self.datetime_service.now()
        payout_factor = self.payout_factor_service.calculate_payout_factor()
        self.payout_factor_service.store_payout_factor(payout_factor)
        expired_plans = self.database_gateway.get_plans().that_are_expired_as_of(now)
        expired_plans.update().set_requested_cooperation(None).set_cooperation(
            None
        ).perform()
