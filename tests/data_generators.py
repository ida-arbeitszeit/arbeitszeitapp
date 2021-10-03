"""The classes in this module should only provide instances of
entities. Never should these entities automatically be added to a
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
    PlanDraft,
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
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
)
from arbeitszeit.use_cases import SeekApproval
from tests.datetime_service import FakeDatetimeService


@inject
@dataclass
class OfferGenerator:
    plan_generator: PlanGenerator
    offer_repository: OfferRepository

    def create_offer(
        self,
        *,
        name="Product name",
        description="",
        plan=None,
    ) -> ProductOffer:
        if plan is None:
            plan = self.plan_generator.create_plan(activation_date=datetime.min)
        return self.offer_repository.create_offer(
            plan=plan,
            creation_datetime=datetime.now(),
            name=name,
            description=description,
        )


@inject
@dataclass
class MemberGenerator:
    account_generator: AccountGenerator
    email_generator: EmailGenerator
    member_repository: MemberRepository

    def create_member(
        self,
        *,
        email: Optional[str] = None,
        account: Optional[Account] = None,
        password: str = "password",
    ) -> Member:
        if not email:
            email = self.email_generator.get_random_email()
        assert email is not None
        if account is None:
            account = self.account_generator.create_account(
                account_type=AccountTypes.member
            )

        return self.member_repository.create_member(
            email=email,
            name="Member name",
            password=password,
            account=account,
        )


@inject
@dataclass
class CompanyGenerator:
    account_generator: AccountGenerator
    company_repository: CompanyRepository
    email_generator: EmailGenerator

    def create_company(
        self,
        *,
        email: Optional[str] = None,
        name: str = "Company Name",
        labour_account: Optional[Account] = None,
        password: str = "password",
    ) -> Company:
        if email is None:
            email = self.email_generator.get_random_email()
        if labour_account is None:
            labour_account = self.account_generator.create_account(
                account_type=AccountTypes.a
            )
        return self.company_repository.create_company(
            email=email,
            name=name,
            password=password,
            means_account=self.account_generator.create_account(
                account_type=AccountTypes.p
            ),
            resource_account=self.account_generator.create_account(
                account_type=AccountTypes.r
            ),
            products_account=self.account_generator.create_account(
                account_type=AccountTypes.prd
            ),
            labour_account=labour_account,
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

    def create_account(self, account_type: AccountTypes = AccountTypes.a) -> Account:
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
    draft_repository: PlanDraftRepository

    def create_plan(
        self,
        *,
        activation_date: Optional[datetime] = None,
        amount: int = 100,
        approved: bool = True,
        costs: Optional[ProductionCosts] = None,
        description="Beschreibung für Produkt A.",
        is_public_service: bool = False,
        plan_creation_date: Optional[datetime] = None,
        planner: Optional[Company] = None,
        product_name: str = "Produkt A",
        production_unit: str = "500 Gramm",
        timeframe: Optional[int] = None,
    ) -> Plan:
        assert approved, "Currently the application does not support plan rejection"
        draft = self.draft_plan(
            planner=planner,
            costs=costs,
            product_name=product_name,
            production_unit=production_unit,
            amount=amount,
            description=description,
            timeframe=timeframe,
            is_public_service=is_public_service,
            plan_creation_date=plan_creation_date,
        )
        self.seek_approval(draft.id, None)
        plan = self.plan_repository.get_plan_by_id(draft.id)
        assert plan
        assert plan.approved
        if activation_date:
            self.plan_repository.activate_plan(plan, activation_date)
        return plan

    def draft_plan(
        self,
        plan_creation_date: Optional[datetime] = None,
        planner: Optional[Company] = None,
        timeframe=None,
        amount: int = 100,
        costs: Optional[ProductionCosts] = None,
        is_public_service: bool = False,
        product_name="Produkt A",
        description="Beschreibung für Produkt A.",
        production_unit="500 Gramm",
    ) -> PlanDraft:
        if plan_creation_date is None:
            plan_creation_date = self.datetime_service.now_minus_two_days()
        if costs is None:
            costs = ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
        if planner is None:
            planner = self.company_generator.create_company()
        if timeframe is None:
            timeframe = 14
        draft = self.draft_repository.create_plan_draft(
            planner=planner.id,
            product_name=product_name,
            description=description,
            costs=costs,
            production_unit=production_unit,
            amount=amount,
            timeframe_in_days=timeframe,
            is_public_service=is_public_service,
            creation_timestamp=plan_creation_date,
        )
        return draft


@inject
@dataclass
class PurchaseGenerator:
    plan_generator: PlanGenerator
    member_generator: MemberGenerator
    company_generator: CompanyGenerator
    datetime_service: FakeDatetimeService
    purchase_repository: PurchaseRepository

    def create_purchase(
        self,
        buyer: Union[Member, Company],
        purchase_date=None,
        amount=1,
    ) -> Purchase:
        if purchase_date is None:
            purchase_date = self.datetime_service.now_minus_one_day()
        return self.purchase_repository.create_purchase(
            purchase_date=purchase_date,
            plan=self.plan_generator.create_plan(),
            buyer=buyer,
            price_per_unit=Decimal(10),
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
        sending_account=None,
        receiving_account=None,
    ) -> Transaction:
        return self.transaction_repository.create_transaction(
            date=self.datetime_service.now_minus_one_day(),
            sending_account=self.account_generator.create_account(
                account_type=sending_account_type
            )
            if None
            else sending_account,
            receiving_account=self.account_generator.create_account(
                account_type=receiving_account_type
            )
            if None
            else receiving_account,
            amount=Decimal(10),
            purpose="Test Verw.zweck",
        )
