from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable, Union
from enum import Enum


class SocialAccounting:
    pass


class Member:
    def __init__(
        self,
        id: int,
    ) -> None:
        self._id = id

    @property
    def id(self):
        return self._id

    def __eq__(self, other: Member) -> bool:
        if isinstance(other, Member):
            return self.id == other.id

        return False


class Company:
    def __init__(
        self,
        id: int,
        means_account: Account,
        raw_material_account: Account,
        work_account: Account,
        product_account: Account,
    ) -> None:
        self._id = id
        self.means_account = means_account
        self.raw_material_account = raw_material_account
        self.work_account = work_account
        self.product_account = product_account

    @property
    def id(self):
        return self._id


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


class Account:
    def __init__(
        self,
        id: int,
        account_owner: Union[SocialAccounting, Member, Company],
        account_type: AccountTypes,
        balance: Decimal,
        change_credit: Callable[[Decimal], None],
    ) -> None:
        self.id = id
        self.account_owner = account_owner
        self.account_type = account_type
        self.balance = balance
        self._change_credit = change_credit

    def change_credit(self, amount: Decimal) -> None:
        self.balance += amount
        self._change_credit(amount)


class Plan:
    def __init__(
        self,
        id: int,
        planner: Company,
        costs_p: Decimal,
        costs_r: Decimal,
        costs_a: Decimal,
        approve: Callable[[bool, str, datetime], None],
    ) -> None:
        self.id = id
        self.planner = planner
        self.costs_p = costs_p
        self.costs_r = costs_r
        self.costs_a = costs_a
        self._approve_call = approve

    def approve(self, approval_date: datetime) -> None:
        self._approve_call(True, "approved", approval_date)

    def deny(self, reason: str, denial_date: datetime) -> None:
        self._approve_call(False, reason, denial_date)


class ProductOffer:
    def __init__(
        self,
        id: int,
        amount_available: int,
        deactivate_offer_in_db: Callable[[], None],
        decrease_amount_available: Callable[[int], None],
        price_per_unit: Decimal,
        provider: Company,
    ) -> None:
        self._id = id
        self._amount_available = amount_available
        self._deactivate = deactivate_offer_in_db
        self._decrease_amount = decrease_amount_available
        self.price_per_unit = price_per_unit
        self.provider = provider

    def deactivate(self) -> None:
        self._deactivate()

    def decrease_amount_available(self, amount: int) -> None:
        self._amount_available -= amount
        self._decrease_amount(amount)

    @property
    def id(self) -> int:
        return self._id

    @property
    def amount_available(self) -> int:
        return self._amount_available


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"


@dataclass
class Purchase:
    purchase_date: datetime
    product_offer: ProductOffer
    buyer: Union[Member, Company]
    price: Decimal
    amount: int
    purpose: PurposesOfPurchases


@dataclass
class Transaction:
    account_from: Account
    account_to: Account
    amount: Decimal
    purpose: str
