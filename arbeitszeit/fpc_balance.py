from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan, Transaction
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class PublicFundService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def calculate_fpc_balance(self) -> Decimal:
        public_plans = (
            self.database_gateway.get_plans().that_are_public().that_are_approved()
        )
        labour_accounts = (
            self.database_gateway.get_accounts().that_are_labour_accounts()
        )
        labour_account_ids = [labour_account.id for labour_account in labour_accounts]

        wage_transactions = (
            self.database_gateway.get_transactions().where_account_is_sender(
                *labour_account_ids
            )
        )

        return calculate_fpc_balance(public_plans, wage_transactions)

    def get_current_fpc_balance(self) -> Decimal:
        return self.calculate_fpc_balance()


def calculate_fpc_balance(
    public_plans: Iterable[Plan], transactions: Iterable[Transaction]
) -> Decimal:
    if public_plans and transactions:
        public_plans_costs = _calculate_public_plans_costs(public_plans=public_plans)
        public_plans_credit = _calculate_public_plans_credit(transactions=transactions)
        return public_plans_credit - public_plans_costs
    elif public_plans and not transactions:
        return _calculate_public_plans_costs(public_plans=public_plans) * -1
    elif not public_plans and transactions:
        return _calculate_public_plans_credit(transactions=transactions)
    else:
        return Decimal(0)


def _calculate_public_plans_costs(public_plans: Iterable[Plan]) -> Decimal:
    return Decimal(
        sum(
            plan.production_costs.resource_cost + plan.production_costs.means_cost
            for plan in public_plans
        )
    )


def _calculate_public_plans_credit(transactions: Iterable[Transaction]) -> Decimal:
    return Decimal(
        sum(
            transaction.amount_sent - transaction.amount_received
            for transaction in transactions
        )
    )
