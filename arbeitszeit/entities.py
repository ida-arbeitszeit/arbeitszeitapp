from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable, Union


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

    @property
    def id(self):
        return self._id


class ProductOffer:
    def __init__(self, id: int, deactivate_offer_in_db: Callable[[], None]) -> None:
        self._id = id
        self._deactivate = deactivate_offer_in_db

    def deactivate(self) -> None:
        self._deactivate()

    @property
    def id(self) -> int:
        return self._id


class Company:
    def __init__(self, id: int, change_credit: Callable[[Decimal], None]) -> None:
        self._id = id
        self._change_credit = change_credit

    def increase_credit(self, amount: Decimal) -> None:
        self._change_credit(amount)

    def reduce_credit(self, amount: Decimal) -> None:
        self._change_credit(-amount)

    @property
    def id(self):
        return self._id


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
        approve_plan: Callable[[], None],   
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
        self._approve = approve_plan

    def approve(self) -> None:
        self._approve()


@dataclass
class PlanApproval:
    approval_date: datetime
    social_accounting: SocialAccounting
    plan: Plan
    approved: bool
    reason: Union[str, None]


@dataclass
class Purchase:
    purchase_date: datetime
    product_offer: ProductOffer
    buyer: Union[Member, Company]
    price: Decimal
