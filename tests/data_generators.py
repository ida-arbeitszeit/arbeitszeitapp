"""The classes in this module should only provide instances of
entities. Never should these entities automatically be added to a
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union
from uuid import uuid4

from injector import inject

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    ProductionCosts,
    ProductOffer,
    Purchase,
    PurposesOfPurchases,
    SocialAccounting,
    Transaction,
)
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
    OfferRepository,
    PlanRepository,
    TransactionRepository,
)
from arbeitszeit.use_cases import SeekApproval
from tests.datetime_service import FakeDatetimeService


@inject
@dataclass
class OfferGenerator:
    plan_generator: PlanGenerator
    offer_repository: OfferRepository
    datetime_service: FakeDatetimeService

    def create_offer(
        self,
        *,
        name="Product name",
        amount=1,
        description="",
        plan=None,
        creation_timestamp=None
    ) -> ProductOffer:
        if plan is None:
            plan = self.plan_generator.create_plan(amount=amount)
        if creation_timestamp is None:
            creation_timestamp = self.datetime_service.now()
        return self.offer_repository.create_offer(
            plan=plan,
            creation_datetime=creation_timestamp,
            name=name,
            description=description,
            amount_available=amount,
        )


@inject
@dataclass
class MemberGenerator:
    account_generator: AccountGenerator
    email_generator: EmailGenerator
    member_repository: MemberRepository

    def create_member(self, *, email: Optional[str] = None) -> Member:
        if not email:
            email = self.email_generator.get_random_email()
        assert email is not None
        return self.member_repository.create_member(
            email=email,
            name="Member name",
            password="password",
            account=self.account_generator.create_account(
                account_type=AccountTypes.member
            ),
        )


@inject
@dataclass
class CompanyGenerator:
    account_generator: AccountGenerator
    company_repository: CompanyRepository
    email_generator: EmailGenerator

    def create_company(self, *, email: Optional[str] = None) -> Company:
        if email is None:
            email = self.email_generator.get_random_email()
        return self.company_repository.create_company(
            email=email,
            name="Company name",
            password="password",
            means_account=self.account_generator.create_account(
                account_type=AccountTypes.p
            ),
            resource_account=self.account_generator.create_account(
                account_type=AccountTypes.r
            ),
            labour_account=self.account_generator.create_account(
                account_type=AccountTypes.a
            ),
            products_account=self.account_generator.create_account(
                account_type=AccountTypes.prd
            ),
        )


@inject
@dataclass
class SocialAccountingGenerator:
    account_generator: AccountGenerator

    def create_social_accounting(self) -> SocialAccounting:
        return SocialAccounting(
            account=self.account_generator.create_account(
                account_type=AccountTypes.accounting
            ),
        )


@inject
@dataclass
class AccountGenerator:
    account_repository: AccountRepository

    def create_account(self, account_type) -> Account:
        return self.account_repository.create_account(account_type)


class EmailGenerator:
    def get_random_email(self):
        return str(uuid4()) + "@cp.org"


@inject
@dataclass
class PlanGenerator:
    company_generator: CompanyGenerator
    datetime_service: FakeDatetimeService
    plan_repository: PlanRepository
    seek_approval: SeekApproval

    def create_plan(
        self,
        plan_creation_date=None,
        planner=None,
        timeframe=None,
        approved=False,
        amount: int = 100,
        total_cost: Optional[Decimal] = None,
        is_public_service=False,
        is_active=False,
        activation_date=None,
    ) -> Plan:
        if total_cost is None:
            total_cost = Decimal(3)
        costs = ProductionCosts(
            labour_cost=total_cost / Decimal(3),
            resource_cost=total_cost / Decimal(3),
            means_cost=total_cost / Decimal(3),
        )
        if plan_creation_date is None:
            plan_creation_date = self.datetime_service.now_minus_two_days()
        if activation_date is None:
            activation_date = self.datetime_service.now_minus_one_day()
        if planner is None:
            planner = self.company_generator.create_company()
        if timeframe is None:
            timeframe = 14
        plan = self.plan_repository.create_plan(
            planner=planner,
            costs=costs,
            product_name="Produkt A",
            production_unit="500 Gramm",
            amount=amount,
            description="Beschreibung für Produkt A.",
            timeframe_in_days=timeframe,
            is_public_service=is_public_service,
            is_active=is_active,
            creation_timestamp=plan_creation_date,
            activation_timestamp=activation_date,
        )
        if approved:
            self.seek_approval(plan, None)
        return plan


@inject
@dataclass
class PurchaseGenerator:
    offer_generator: OfferGenerator
    member_generator: MemberGenerator
    company_generator: CompanyGenerator
    datetime_service: FakeDatetimeService

    def create_purchase(
        self,
        buyer: Union[Member, Company],
        purchase_date=None,
        amount=1,
    ) -> Purchase:
        if purchase_date is None:
            purchase_date = self.datetime_service.now_minus_one_day()
        return Purchase(
            purchase_date=purchase_date,
            product_offer=self.offer_generator.create_offer(),
            buyer=buyer,
            price=Decimal(10),
            amount=amount,
            purpose=PurposesOfPurchases.consumption,
        )


@inject
@dataclass
class TransactionGenerator:
    account_generator: AccountGenerator
    transaction_repository: TransactionRepository
    datetime_service: FakeDatetimeService

    def create_transaction(
        self,
        sending_account_type=AccountTypes.p,
        receiving_account_type=AccountTypes.prd,
        account_from=None,
        account_to=None,
    ) -> Transaction:
        return self.transaction_repository.create_transaction(
            date=self.datetime_service.now_minus_one_day(),
            account_from=self.account_generator.create_account(
                account_type=sending_account_type
            )
            if None
            else account_from,
            account_to=self.account_generator.create_account(
                account_type=receiving_account_type
            )
            if None
            else account_to,
            amount=Decimal(10),
            purpose="Test Verw.zweck",
        )
