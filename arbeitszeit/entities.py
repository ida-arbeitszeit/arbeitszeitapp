from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable, Union, Optional


class SocialAccounting:
    def __init__(self, id: int) -> None:
        self._id = id

    @property
    def id(self):
        return self._id


class Member:
    def __init__(self, id: int, change_credit: Callable[[Decimal], None]) -> None:
        self._change_credit = change_credit
        self._id = id

    def reduce_credit(self, amount: Decimal) -> None:
        self._change_credit(-amount)

    def increase_credit(self, amount: Decimal) -> None:
        self._change_credit(amount)

    @property
    def id(self):
        return self._id


class ProductOffer:
    def __init__(
        self,
        id: int,
        amount_available: int,
        deactivate_offer_in_db: Callable[[], None],
        decrease_amount_available: Callable[[int], None],
    ) -> None:
        self._id = id
        self._amount_available = amount_available
        self._deactivate = deactivate_offer_in_db
        self._decrease_amount = decrease_amount_available

    def deactivate(self) -> None:
        self._deactivate()

    def decrease_amount_available(self, amount: int) -> None:
        self._decrease_amount(amount)

    @property
    def id(self) -> int:
        return self._id

    @property
    def amount_available(self) -> int:
        return self._amount_available


class Company:
    def __init__(self, id: int, change_credit: Callable[[Decimal, str], None]) -> None:
        self._id = id
        self._change_credit = change_credit

    def increase_credit(self, amount: Decimal, account_type: str) -> None:
        self._change_credit(amount, account_type)

    def reduce_credit(self, amount: Decimal, account_type: str) -> None:
        self._change_credit(-amount, account_type)

    @property
    def id(self):
        return self._id


@dataclass
class Plan:
    id: int
    approve: Callable[[bool, str, datetime], None]


@dataclass
class Purchase:
    purchase_date: datetime
    product_offer: ProductOffer
    buyer: Union[Member, Company]
    price: Decimal
    amount: int
    purpose: str


@dataclass
class Transaction:
    account_owner: Union[SocialAccounting, Member, Company]
    receiver: Union[Member, Company]
    amount: Decimal
