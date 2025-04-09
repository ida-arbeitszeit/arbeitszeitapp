from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.records import Plan, SocialAccounting, Transfer
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PublicSectorFundService:
    database_gateway: DatabaseGateway
    social_accounting: SocialAccounting

    def calculate_psf_balance(self) -> Decimal:
        public_plans = (
            self.database_gateway.get_plans().that_are_public().that_are_approved()
        )
        taxes_transfers = (
            self.database_gateway.get_transfers().where_account_is_creditor(
                self.social_accounting.account_psf
            )
        )
        public_plans_costs = self._calculate_public_plans_costs(
            public_plans=public_plans
        )
        taxes = self._calculate_sum_of_taxes(taxes_transfers=taxes_transfers)
        return taxes - public_plans_costs

    def _calculate_public_plans_costs(self, public_plans: Iterable[Plan]) -> Decimal:
        return decimal_sum(
            plan.production_costs.resource_cost + plan.production_costs.means_cost
            for plan in public_plans
        )

    def _calculate_sum_of_taxes(self, taxes_transfers: Iterable[Transfer]) -> Decimal:
        return decimal_sum(transfer.value for transfer in taxes_transfers)
