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

from arbeitszeit.datetime_service import DatetimeService
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
from tests.datetime_service import TestDatetimeService
from tests.repositories import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
    TransactionRepository,
)


@inject
@dataclass
class OfferGenerator:
    company_generator: CompanyGenerator

    def create_offer(
        self, *, name="Product name", amount=1, provider=None, description=""
    ):
        return ProductOffer(
            id=uuid4(),
            name=name,
            amount_available=amount,
            deactivate_offer_in_db=lambda: None,
            decrease_amount_available=lambda _: None,
            price_per_unit=Decimal(1),
            provider=self.company_generator.create_company()
            if provider is None
            else provider,
            active=True,
            description=description,
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

    def create_company(self) -> Company:
        return self.company_repository.create_company(
            email=self.email_generator.get_random_email(),
            name="Company name",
            password="password",
            means_account=self.account_generator.create_account(
                account_type=AccountTypes.p
            ),
            resources_account=self.account_generator.create_account(
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
    datetime_service: DatetimeService

    def create_plan(
        self, plan_creation_date=None, planner=None, timeframe=None, approved=False
    ) -> Plan:
        costs = ProductionCosts(
            means_cost=Decimal(10),
            resource_cost=Decimal(20),
            labour_cost=Decimal(30),
        )
        return Plan(
            id=uuid4(),
            plan_creation_date=self.datetime_service.now()
            if plan_creation_date is None
            else plan_creation_date,
            planner=self.company_generator.create_company()
            if planner is None
            else planner,
            prd_name="Produkt A",
            prd_unit="500 Gramm",
            prd_amount=100,
            production_costs=costs,
            description="Beschreibung für Produkt A.",
            timeframe=int(14) if timeframe is None else int(timeframe),
            approved=approved,
            approval_date=None,
            approval_reason=None,
            approve=lambda _1, _2, _3: None,
            expired=False,
            renewed=False,
            set_as_expired=lambda: None,
            set_as_renewed=lambda: None,
            expiration_relative=None,
            expiration_date=None,
        )


@inject
@dataclass
class PurchaseGenerator:
    offer_generator: OfferGenerator
    member_generator: MemberGenerator
    company_generator: CompanyGenerator

    def create_purchase(
        self,
        buyer: Union[Member, Company],
        purchase_date=TestDatetimeService().now_minus_one_day(),
        amount=1,
    ) -> Purchase:
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

    def create_transaction(
        self,
        sending_account_type=AccountTypes.p,
        receiving_account_type=AccountTypes.prd,
        account_from=None,
        account_to=None,
    ) -> Transaction:
        return self.transaction_repository.create_transaction(
            date=TestDatetimeService().now_minus_one_day(),
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
