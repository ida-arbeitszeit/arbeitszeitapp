from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, Union


class Member:
    def __init__(self, id: int, reduce_credit_in_db: Callable[[Decimal], None]) -> None:
        self._reduce_credit_in_db = reduce_credit_in_db
        self._id = id

    def reduce_credit(self, amount: Decimal) -> None:
        self._reduce_credit_in_db(amount)

    @property
    def id(self):
        return self._id


class ProductOffer:
    def __init__(
        self, id: int, deactivate_offer_in_db: Callable[[], None]
    ) -> None:
        self._id = id
        self._deactivate = deactivate_offer_in_db

    def deactivate(self) -> None:
        self._deactivate()

    @property
    def id(self) -> int:
        return self._id


class Company:
    def __init__(self, id: int, increase_credit: Callable[[Decimal], None]) -> None:
        self._id = id
        self._increase_credit = increase_credit

    def increase_credit(self, amount: Decimal) -> None:
        self._increase_credit(amount)

    @property
    def id(self):
        return self._id


@dataclass
class Purchase:
    purchase_date: datetime
    product_offer: ProductOffer
    buyer: Union[Member, Company]
    price: Decimal
