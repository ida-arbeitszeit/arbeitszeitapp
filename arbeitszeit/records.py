from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID


@dataclass
class EmailAddress:
    address: str
    confirmed_on: Optional[datetime]


@dataclass
class SocialAccounting:
    id: UUID
    account: UUID

    def get_name(self) -> str:
        return "Social Accounting"

    def get_account_type(self, account: UUID) -> Optional[AccountTypes]:
        if account == self.account:
            return AccountTypes.accounting
        return None

    def is_member(self) -> bool:
        return False


@dataclass
class Member:
    id: UUID
    name: str
    account: UUID
    registered_on: datetime

    def accounts(self) -> List[UUID]:
        return [self.account]

    def get_name(self) -> str:
        return self.name

    def get_account_by_type(self, account_type: AccountTypes) -> Optional[UUID]:
        if account_type == AccountTypes.member:
            return self.account
        return None

    def get_account_type(self, account: UUID) -> Optional[AccountTypes]:
        if self.account == account:
            return AccountTypes.member
        else:
            return None

    def is_member(self) -> bool:
        return True


@dataclass
class Company:
    id: UUID
    name: str
    means_account: UUID
    raw_material_account: UUID
    work_account: UUID
    product_account: UUID
    registered_on: datetime

    def _accounts_by_type(self) -> Dict[AccountTypes, UUID]:
        return {
            AccountTypes.p: self.means_account,
            AccountTypes.r: self.raw_material_account,
            AccountTypes.a: self.work_account,
            AccountTypes.prd: self.product_account,
        }

    def accounts(self) -> List[UUID]:
        return list(self._accounts_by_type().values())

    def get_name(self) -> str:
        return self.name

    def get_account_by_type(self, account_type: AccountTypes) -> Optional[UUID]:
        return self._accounts_by_type().get(account_type)

    def get_account_type(self, account: UUID) -> Optional[AccountTypes]:
        account_types = {
            self.means_account: AccountTypes.p,
            self.raw_material_account: AccountTypes.r,
            self.work_account: AccountTypes.a,
            self.product_account: AccountTypes.prd,
        }
        return account_types.get(account)

    def is_member(self) -> bool:
        return False


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


@dataclass(frozen=True)
class Account:
    id: UUID


@dataclass
class Cooperation:
    id: UUID
    creation_date: datetime
    name: str
    definition: str


@dataclass
class CoordinationTenure:
    id: UUID
    company: UUID
    cooperation: UUID
    start_date: datetime


@dataclass
class CoordinationTransferRequest:
    id: UUID
    requesting_coordination_tenure: UUID
    candidate: UUID
    request_date: datetime


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

    @classmethod
    def zero(cls) -> ProductionCosts:
        return cls(Decimal(0), Decimal(0), Decimal(0))


@dataclass
class PlanDraft:
    id: UUID
    creation_date: datetime
    planner: UUID
    production_costs: ProductionCosts
    product_name: str
    unit_of_distribution: str
    amount_produced: int
    description: str
    timeframe: int
    is_public_service: bool

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


@dataclass
class Plan:
    id: UUID
    plan_creation_date: datetime
    planner: UUID
    production_costs: ProductionCosts
    prd_name: str
    prd_unit: str
    prd_amount: int
    description: str
    timeframe: int
    is_public_service: bool
    approval_date: Optional[datetime]
    rejection_date: Optional[datetime]
    activation_date: Optional[datetime]
    requested_cooperation: Optional[UUID]
    hidden_by_user: bool

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

    @property
    def is_approved(self) -> bool:
        return self.approval_date is not None and self.rejection_date is None

    @property
    def is_rejected(self) -> bool:
        return self.rejection_date is not None and self.approval_date is None

    @property
    def expiration_date(self) -> Optional[datetime]:
        if not self.activation_date:
            return None
        exp_date = self.activation_date + timedelta(days=int(self.timeframe))
        return exp_date

    def active_days(self, reference_timestamp: datetime) -> Optional[int]:
        """Returns the full days a plan would be active at the
        specified timestamp, not considering days exceeding it's
        timeframe.
        """
        if not self.activation_date:
            return None
        days_passed_since_activation = (reference_timestamp - self.activation_date).days
        return min(self.timeframe, days_passed_since_activation)

    def is_active_as_of(self, timestamp: datetime) -> bool:
        return (
            self.activation_date is not None
            and self.activation_date <= timestamp
            and not self.is_expired_as_of(timestamp)
        )

    def is_expired_as_of(self, timestamp: datetime) -> bool:
        return self.expiration_date is not None and timestamp >= self.expiration_date

    def to_summary(self) -> PlanSummary:
        return PlanSummary(
            production_costs=self.production_costs.total_cost(),
            duration_in_days=self.timeframe,
            amount=self.prd_amount,
        )

    def cost_per_unit(self) -> Decimal:
        if self.prd_amount == 0:
            return Decimal(0)
        return self.production_costs.total_cost() / Decimal(self.prd_amount)

    def price_per_unit(self) -> Decimal:
        return Decimal(0) if self.is_public_service else self.cost_per_unit()


class ConsumptionType(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


@dataclass
class Transaction:
    """
    The amount received by a transaction can differ from the amount sent.
    This is e.g. the case when a product is paid. Then the amount sent is defined by
    the current coop_price, while the amount received (by the prd-account of the company)
    is defined by the originally planned costs for the product.
    """

    id: UUID
    date: datetime
    sending_account: UUID
    receiving_account: UUID
    amount_sent: Decimal
    amount_received: Decimal
    purpose: str

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class CompanyWorkInvite:
    id: UUID
    company: UUID
    member: UUID


@dataclass
class Accountant:
    id: UUID
    name: str


@dataclass
class PlanningStatistics:
    average_plan_duration_in_days: Decimal
    total_planned_costs: ProductionCosts


@dataclass(frozen=True)
class PrivateConsumption:
    id: UUID
    plan_id: UUID
    transaction_id: UUID
    amount: int


@dataclass(frozen=True)
class ProductiveConsumption:
    id: UUID
    plan_id: UUID
    transaction_id: UUID
    amount: int


AccountOwner = Union[Member, Company, SocialAccounting]


@dataclass
class AccountCredentials:
    id: UUID
    email_address: str
    password_hash: str


@dataclass
class PlanSummary:
    production_costs: Decimal
    duration_in_days: int
    amount: int


@dataclass
class PasswordResetRequest:
    id: UUID
    email_address: str
    reset_token: str
    created_at: datetime


@dataclass
class RegisteredHoursWorked:
    id: UUID
    company: UUID
    member: UUID
    amount: Decimal
    transaction: UUID
    registered_on: datetime


@dataclass
class CancelledHoursWorked:
    id: UUID
    registered_entry: UUID
    transaction: UUID
    cancelled_on: datetime
