from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.user_action import UserAction


@dataclass
class SocialAccounting:
    id: UUID
    account: Account


@dataclass
class Member:
    id: UUID
    name: str
    email: str
    account: Account

    def accounts(self) -> List[Account]:
        return [self.account]


@dataclass
class Company:
    id: UUID
    email: str
    name: str
    means_account: Account
    raw_material_account: Account
    work_account: Account
    product_account: Account

    def accounts(self) -> List[Account]:
        return [
            self.means_account,
            self.raw_material_account,
            self.work_account,
            self.product_account,
        ]


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


@dataclass
class Account:
    id: UUID
    account_type: AccountTypes


@dataclass
class MetaProduct:
    id: UUID
    creation_date: datetime
    name: str
    definition: str
    coordinator: Company
    plans: List[Plan]  # should not include public plans

    @property
    def meta_price_per_unit(self) -> Decimal:
        meta_price_per_unit = (
            decimal_sum([plan.production_costs.total_cost() for plan in self.plans])
        ) / (sum([plan.prd_amount for plan in self.plans]) or 1)
        return meta_price_per_unit


@dataclass
class ProductionCosts:
    labour_cost: Decimal
    resource_cost: Decimal
    means_cost: Decimal

    def total_cost(self) -> Decimal:
        return self.labour_cost + self.resource_cost + self.means_cost

    def __truediv__(self, other: Union[int, float]) -> ProductionCosts:
        denominator = Decimal(other)
        return ProductionCosts(
            labour_cost=self.labour_cost / denominator,
            resource_cost=self.resource_cost / denominator,
            means_cost=self.means_cost / denominator,
        )

    def __add__(self, other: ProductionCosts) -> ProductionCosts:
        return ProductionCosts(
            labour_cost=self.labour_cost + other.labour_cost,
            resource_cost=self.resource_cost + other.resource_cost,
            means_cost=self.means_cost + other.means_cost,
        )


@dataclass
class PlanDraft:
    id: UUID
    creation_date: datetime
    planner: Company
    production_costs: ProductionCosts
    product_name: str
    unit_of_distribution: str
    amount_produced: int
    description: str
    timeframe: int
    is_public_service: bool


@dataclass
class Plan:
    id: UUID
    plan_creation_date: datetime
    planner: Company
    production_costs: ProductionCosts
    prd_name: str
    prd_unit: str
    prd_amount: int
    description: str
    timeframe: int
    is_public_service: bool
    approved: bool
    approval_date: Optional[datetime]
    approval_reason: Optional[str]
    is_active: bool
    expired: bool
    renewed: bool
    activation_date: Optional[datetime]
    expiration_relative: Optional[int]
    expiration_date: Optional[datetime]
    active_days: Optional[int]
    payout_count: int
    meta_product: Optional[MetaProduct]

    @property
    def individual_price_per_unit(self) -> Decimal:
        return (
            self.production_costs.total_cost() / self.prd_amount
            if not self.is_public_service
            else Decimal(0)
        )

    @property
    def price_per_unit(self) -> Decimal:
        if self.meta_product is None:
            price_per_unit = self.individual_price_per_unit
        else:
            price_per_unit = self.meta_product.meta_price_per_unit
        return price_per_unit

    @property
    def expected_sales_value(self) -> Decimal:
        """
        For productive plans, sales value should equal total cost.
        Public services are not expected to sell,
        they give away their product for free.
        """
        return (
            self.production_costs.total_cost()
            if not self.is_public_service
            else Decimal(0)
        )


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


@dataclass
class Purchase:
    purchase_date: datetime
    plan: Plan
    buyer: Union[Member, Company]
    price_per_unit: Decimal
    amount: int
    purpose: PurposesOfPurchases


@dataclass
class Transaction:
    id: UUID
    date: datetime
    sending_account: Account
    receiving_account: Account
    amount: Decimal
    purpose: str

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class CompanyWorkInvite:
    company: Company
    member: Member


@dataclass
class Message:
    id: UUID
    sender: Union[Member, Company, SocialAccounting]
    addressee: Union[Member, Company]
    title: str
    content: str
    sender_remarks: Optional[str]
    user_action: Optional[UserAction]
    is_read: bool
