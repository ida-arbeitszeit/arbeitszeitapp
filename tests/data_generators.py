"""The classes in this module should only provide instances of
entities. Never should these entities automatically be added to a
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Optional, Union
from uuid import UUID, uuid4

from injector import inject

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Cooperation,
    Member,
    Plan,
    PlanDraft,
    ProductionCosts,
    Purchase,
    PurposesOfPurchases,
    SocialAccounting,
    Transaction,
    WorkerInviteMessage,
)
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    CooperationRepository,
    MemberRepository,
    PlanCooperationRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    WorkerInviteMessageRepository,
)
from arbeitszeit.use_cases import (
    AcceptCooperation,
    AcceptCooperationRequest,
    RequestCooperation,
    RequestCooperationRequest,
    SeekApproval,
)
from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.company import CompanyManager
from tests.datetime_service import FakeDatetimeService


@inject
@dataclass
class MemberGenerator:
    account_generator: AccountGenerator
    email_generator: EmailGenerator
    member_repository: MemberRepository
    datetime_service: FakeDatetimeService

    def create_member(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        account: Optional[Account] = None,
        password: str = "password",
        registered_on: datetime = None,
    ) -> Member:
        if not email:
            email = self.email_generator.get_random_email()
        assert email is not None
        if account is None:
            account = self.account_generator.create_account(
                account_type=AccountTypes.member
            )
        if registered_on is None:
            registered_on = self.datetime_service.now()

        return self.member_repository.create_member(
            email=email,
            name=name,
            password=password,
            account=account,
            registered_on=registered_on,
        )


@inject
@dataclass
class CompanyGenerator:
    account_generator: AccountGenerator
    company_repository: CompanyRepository
    email_generator: EmailGenerator
    datetime_service: FakeDatetimeService
    company_manager: CompanyManager

    def create_company(
        self,
        *,
        email: Optional[str] = None,
        name: str = "Company Name",
        labour_account: Optional[Account] = None,
        password: str = "password",
        workers: Optional[Iterable[Member]] = None,
        registered_on: datetime = None,
    ) -> Company:
        if email is None:
            email = self.email_generator.get_random_email()
        if labour_account is None:
            labour_account = self.account_generator.create_account(
                account_type=AccountTypes.a
            )
        if registered_on is None:
            registered_on = self.datetime_service.now()
        company = self.company_repository.create_company(
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
            registered_on=registered_on,
        )
        if workers is not None:
            for worker in workers:
                self.company_manager.add_worker_to_company(company.id, worker.id)
        return company


@inject
@dataclass
class SocialAccountingGenerator:
    account_generator: AccountGenerator

    def create_social_accounting(self) -> SocialAccounting:
        return SocialAccounting(
            id=uuid4(),
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
    request_cooperation: RequestCooperation
    accept_cooperation: AcceptCooperation
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
        expired: bool = False,
        requested_cooperation: Optional[Cooperation] = None,
        cooperation: Optional[Cooperation] = None,
        is_available: bool = True,
        hidden_by_user: bool = False,
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
        response = self.seek_approval(SeekApproval.Request(draft_id=draft.id))
        plan = self.plan_repository.get_plan_by_id(response.new_plan_id)
        assert plan
        assert plan.is_approved
        if activation_date:
            self.plan_repository.activate_plan(plan, activation_date)
        if expired:
            self.plan_repository.set_plan_as_expired(plan)
        if requested_cooperation:
            self.request_cooperation(
                RequestCooperationRequest(
                    plan.planner.id, plan.id, requested_cooperation.id
                )
            )
        if cooperation:
            self.request_cooperation(
                RequestCooperationRequest(plan.planner.id, plan.id, cooperation.id)
            )
            self.accept_cooperation(
                AcceptCooperationRequest(
                    cooperation.coordinator.id, plan.id, cooperation.id
                )
            )
        if hidden_by_user:
            self.plan_repository.hide_plan(plan.id)
        if not is_available:
            self.plan_repository.toggle_product_availability(plan)
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
        amount_sent=None,
        amount_received=None,
        purpose=None,
    ) -> Transaction:
        if sending_account is None:
            sending_account = self.account_generator.create_account(
                account_type=sending_account_type
            )
        if receiving_account is None:
            receiving_account = self.account_generator.create_account(
                account_type=receiving_account_type
            )
        if amount_sent is None:
            amount_sent = Decimal(10)
        if amount_received is None:
            amount_received = Decimal(10)
        if purpose is None:
            purpose = "test purpose"
        return self.transaction_repository.create_transaction(
            date=self.datetime_service.now_minus_one_day(),
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )


@inject
@dataclass
class CooperationGenerator:
    cooperation_repository: CooperationRepository
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    plan_cooperation_repository: PlanCooperationRepository

    def create_cooperation(
        self,
        name: str = None,
        coordinator: Optional[Company] = None,
        plans: List[Plan] = None,
    ) -> Cooperation:
        if name is None:
            name = "test name"
        if coordinator is None:
            coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_repository.create_cooperation(
            self.datetime_service.now(),
            name=name,
            definition="test info",
            coordinator=coordinator,
        )
        if plans is not None:
            for plan in plans:
                self.plan_cooperation_repository.add_plan_to_cooperation(
                    plan.id, cooperation.id
                )
        return cooperation


@inject
@dataclass
class WorkerInviteMessageGenerator:
    worker_invite_message_repository: WorkerInviteMessageRepository
    company_generator: CompanyGenerator
    member_generator: MemberGenerator

    def create_message(
        self,
        invite_id: UUID = None,
        company: Company = None,
        worker: Member = None,
        creation_date: datetime = None,
    ) -> WorkerInviteMessage:
        if invite_id is None:
            invite_id = uuid4()
        if company is None:
            company = self.company_generator.create_company()
        if worker is None:
            worker = self.member_generator.create_member()
        if creation_date is None:
            creation_date = datetime.now()
        return self.worker_invite_message_repository.create_message(
            invite_id, company, worker, creation_date
        )


@inject
@dataclass
class AccountantGenerator:
    invite_accountant_use_case: SendAccountantRegistrationTokenUseCase
    invite_accountant_presenter: AccountantInvitationPresenterTestImpl
    register_accountant_use_case: RegisterAccountantUseCase
    email_generator: EmailGenerator

    def create_accountant(
        self,
        *,
        email_address: Optional[str] = None,
        name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> UUID:
        if email_address is None:
            email_address = self.email_generator.get_random_email()
        if name is None:
            name = "user name test"
        if password is None:
            password = "password123"
        self.invite_accountant_use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(email=email_address)
        )
        token = self.invite_accountant_presenter.invitations[-1].token
        response = self.register_accountant_use_case.register_accountant(
            request=RegisterAccountantUseCase.Request(
                name=name,
                email=email_address,
                token=token,
                password=password,
            )
        )
        assert response.is_accepted
        user_id = response.user_id
        assert user_id is not None
        return user_id
