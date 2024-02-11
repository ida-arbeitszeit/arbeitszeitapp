from __future__ import annotations

from enum import Enum, auto
from typing import Iterable, Optional, Tuple, TypeAlias

from arbeitszeit.records import AccountTypes


class TransactionTypes(Enum):
    """Transaction types from the perspective of the account owner."""

    credit_for_wages = auto()
    payment_of_wages = auto()
    incoming_wages = auto()
    credit_for_fixed_means = auto()
    consumption_of_fixed_means = auto()
    credit_for_liquid_means = auto()
    consumption_of_liquid_means = auto()
    expected_sales = auto()
    sale_of_consumer_product = auto()
    private_consumption = auto()
    sale_of_fixed_means = auto()
    sale_of_liquid_means = auto()

    @classmethod
    def for_sender(
        cls, sender: AccountTypes, receiver: AccountTypes
    ) -> Optional[TransactionTypes]:
        return _rules_for_sender.get(sender, receiver)

    @classmethod
    def for_receiver(
        cls, sender: AccountTypes, receiver: AccountTypes
    ) -> Optional[TransactionTypes]:
        return _rules_for_receiver.get(sender, receiver)


# These type aliases are created for a convenient notation of
# transaction type rules down belore.
at: TypeAlias = AccountTypes
tt: TypeAlias = TransactionTypes
Rule: TypeAlias = Tuple[
    Tuple[Optional[AccountTypes], Optional[AccountTypes]], TransactionTypes
]


class _Rules:
    """Check a given combination of sender and receiver accounts
    agains the provided ruleset. The first rule that matches will be
    used.
    """

    def __init__(
        self,
        rules: Iterable[Rule],
    ) -> None:
        self.rules = list(rules)

    def get(
        self, sender: AccountTypes, receiver: AccountTypes
    ) -> Optional[TransactionTypes]:
        for (sender_pattern, receiver_pattern), result in self.rules:
            if (sender_pattern is None or sender == sender_pattern) and (
                receiver_pattern is None or receiver_pattern == receiver
            ):
                return result
        return None


any_type = None


# These rules describe how a transaction should be classified based on
# the involved account types.  Rules are evaluated in order.
_rules_for_sender = _Rules(
    [
        ((at.a, any_type), tt.payment_of_wages),
        ((at.p, any_type), tt.consumption_of_fixed_means),
        ((at.r, any_type), tt.consumption_of_liquid_means),
        ((at.member, any_type), tt.private_consumption),
    ]
)

_rules_for_receiver = _Rules(
    [
        ((at.accounting, at.a), tt.credit_for_wages),
        ((at.accounting, at.p), tt.credit_for_fixed_means),
        ((at.accounting, at.r), tt.credit_for_liquid_means),
        ((at.accounting, at.prd), tt.expected_sales),
        ((at.accounting, at.member), tt.incoming_wages),
        ((at.p, any_type), tt.sale_of_fixed_means),
        ((at.r, any_type), tt.sale_of_liquid_means),
        ((at.a, any_type), tt.incoming_wages),
        ((at.member, any_type), tt.sale_of_consumer_product),
    ]
)
