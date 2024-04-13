from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan, Transaction
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PublicFundService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def calculate_fpc_balance(self, timestamp: datetime) -> Decimal:
        public_plans = (
            self.database_gateway.get_plans()
            .that_are_public()
            .that_are_approved()
        )
        print(f"public plans: {public_plans}")

        labour_accounts = (
            self.database_gateway.get_accounts()
            .that_are_labour_accounts()
        )
        print(f"labour_accounts: {labour_accounts}")

        lohn_transactions = (
            self.database_gateway.get_transactions()
            .where_sender_is_labour_account(labour_accounts)
        )
        print(f"lohn_transactions: {lohn_transactions}")

        return calculate_fpc_balance(public_plans, lohn_transactions)

    def get_current_fpc_balance(self) -> Decimal:
        now = self.datetime_service.now()
        return self.calculate_fpc_balance(now)


def calculate_fpc_balance(public_plans: Iterable[Plan], transactions: Iterable[Transaction]) -> Decimal:
    public_plans_costs = sum(plan.production_costs.resource_cost + plan.production_costs.means_cost for plan in public_plans)
    print(f"public_plans_costs: {public_plans_costs}")
    public_plans_credit = sum(1 - transaction.amount_received for transaction in transactions)
    print(f"public_plans_credit: {public_plans_credit}")
    return public_plans_credit - public_plans_costs
