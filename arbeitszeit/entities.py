from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Callable, List, Optional, Union


@dataclass
class SocialAccounting:
    account: Account


class Member:
    def __init__(
        self,
        id: int,
        name: str,
        email: str,
        account: Account,
    ) -> None:
        self._id = id
        self.name = name
        self.account = account
        self.email = email

    @property
    def id(self):
        return self._id

    def __eq__(self, other: object) -> bool:
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
        workers: List[Member],
    ) -> None:
        self._id = id
        self.means_account = means_account
        self.raw_material_account = raw_material_account
        self.work_account = work_account
        self.product_account = product_account
        self.workers = workers

    @property
    def id(self):
        return self._id

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Company):
            return self.id == other.id

        return False


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
        account_type: AccountTypes,
        balance: Decimal,
        change_credit: Callable[[Decimal], None],
    ) -> None:
        self.id = id
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
        plan_creation_date: datetime,
        planner: Company,
        costs_p: Decimal,
        costs_r: Decimal,
        costs_a: Decimal,
        prd_name: str,
        prd_unit: str,
        prd_amount: int,
        description: str,
        timeframe: int,
        approved: bool,
        approval_date: Optional[datetime],
        approval_reason: Optional[str],
        approve: Callable[[bool, str, datetime], None],
        expired: bool,
        renewed: bool,
        set_as_expired: Callable[[], None],
        set_as_renewed: Callable[[], None],
    ) -> None:
        self.id = id
        self.plan_creation_date = plan_creation_date
        self.planner = planner
        self.costs_p = costs_p
        self.costs_r = costs_r
        self.costs_a = costs_a
        self.prd_name = prd_name
        self.prd_unit = prd_unit
        self.prd_amount = prd_amount
        self.description = description
        self.timeframe = timeframe
        self.approved = approved
        self.approval_date = approval_date
        self.approval_reason = approval_reason
        self._approve_call = approve
        self.expired = expired
        self.renewed = renewed
        self._set_as_expired = set_as_expired
        self._set_as_renewed = set_as_renewed

    def approve(self, approval_date: datetime) -> None:
        self.approved = True
        self.approval_date = approval_date
        self.approval_reason = "approved"
        self._approve_call(True, "approved", approval_date)

    def deny(self, denial_date: datetime) -> None:
        self.approved = False
        self.approval_date = denial_date
        self.approval_reason = "not approved"
        self._approve_call(False, "not approved", denial_date)

    def set_as_expired(self) -> None:
        self.expired = True
        self._set_as_expired()

    def set_as_renewed(self) -> None:
        self.renewed = True
        self._set_as_renewed()


@dataclass
class PlanRenewal:
    original_plan: Plan
    modifications: bool


class ProductOffer:
    def __init__(
        self,
        id: int,
        name: str,
        amount_available: int,
        deactivate_offer_in_db: Callable[[], None],
        decrease_amount_available: Callable[[int], None],
        price_per_unit: Decimal,
        provider: Company,
        active: bool,
        description: str,
    ) -> None:
        self._id = id
        self.name = name
        self._amount_available = amount_available
        self._deactivate = deactivate_offer_in_db
        self._decrease_amount = decrease_amount_available
        self.price_per_unit = price_per_unit
        self.provider = provider
        self.active = active
        self.description = description

    def deactivate(self) -> None:
        self.active = False
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
    consumption = "consumption"


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

    def adjust_balances(self) -> None:
        """this method adjusts the balances of the two accounts
        that are involved in this transaction."""
        self.account_from.change_credit(-self.amount)
        self.account_to.change_credit(self.amount)
