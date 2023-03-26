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

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Cooperation,
    Member,
    Plan,
    PlanDraft,
    ProductionCosts,
    PurposesOfPurchases,
    Transaction,
)
from arbeitszeit.repositories import (
    AccountRepository,
    CompanyRepository,
    CooperationRepository,
    DatabaseGateway,
    MemberRepository,
    PlanDraftRepository,
    TransactionRepository,
)
from arbeitszeit.use_cases import pay_consumer_product, pay_means_of_production
from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.create_plan_draft import (
    CreatePlanDraft,
    CreatePlanDraftRequest,
)
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit.use_cases.request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
)
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.company import CompanyManager
from tests.datetime_service import FakeDatetimeService


@dataclass
class MemberGenerator:
    account_generator: AccountGenerator
    email_generator: EmailGenerator
    member_repository: MemberRepository
    datetime_service: FakeDatetimeService
    register_member_use_case: RegisterMemberUseCase

    def create_member_entity(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        account: Optional[Account] = None,
        password: str = "password",
        registered_on: Optional[datetime] = None,
        confirmed: bool = True,
    ) -> Member:
        if not email:
            email = self.email_generator.get_random_email()
        assert email is not None
        if not confirmed:
            response = self.register_member_use_case.register_member(
                request=RegisterMemberUseCase.Request(
                    email=email, name=name, password=password
                )
            )
            assert not response.is_rejected
            member = (
                self.member_repository.get_members().with_email_address(email).first()
            )
            assert member
            return member
        if account is None:
            account = self.account_generator.create_account(
                account_type=AccountTypes.member
            )
        if registered_on is None:
            registered_on = self.datetime_service.now()
        member = self.member_repository.create_member(
            email=email,
            name=name,
            password=password,
            account=account,
            registered_on=registered_on,
        )
        assert (
            self.member_repository.get_members()
            .with_id(member.id)
            .update()
            .set_confirmation_timestamp(registered_on)
            .perform()
        )
        member = self.member_repository.get_members().with_id(member.id).first()
        assert member
        return member

    def create_member(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        account: Optional[Account] = None,
        password: str = "password",
        registered_on: Optional[datetime] = None,
        confirmed: bool = True,
    ) -> UUID:
        member = self.create_member_entity(
            email=email,
            name=name,
            password=password,
            account=account,
            registered_on=registered_on,
            confirmed=confirmed,
        )
        return member.id


@dataclass
class CompanyGenerator:
    account_generator: AccountGenerator
    company_repository: CompanyRepository
    email_generator: EmailGenerator
    datetime_service: FakeDatetimeService
    company_manager: CompanyManager
    register_company_use_case: RegisterCompany

    def create_company_entity(
        self,
        *,
        email: Optional[str] = None,
        name: str = "Company Name",
        password: str = "password",
        workers: Optional[Iterable[Union[Member, UUID]]] = None,
        registered_on: Optional[datetime] = None,
    ) -> Company:
        if email is None:
            email = self.email_generator.get_random_email()
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
            labour_account=self.account_generator.create_account(
                account_type=AccountTypes.a
            ),
            registered_on=registered_on,
        )
        if workers is not None:
            for worker in workers:
                if isinstance(worker, UUID):
                    self.company_manager.add_worker_to_company(company.id, worker)
                else:
                    self.company_manager.add_worker_to_company(company.id, worker.id)
        return company

    def create_company(
        self,
        *,
        name: str = "test company",
        confirmed: bool = True,
        email: Optional[str] = None,
        password: Optional[str] = None,
        workers: Optional[Iterable[UUID]] = None,
    ) -> UUID:
        if email is None:
            email = self.email_generator.get_random_email()
        if password is None:
            password = "test password"
        response = self.register_company_use_case.register_company(
            request=RegisterCompany.Request(
                name=name,
                email=email,
                password=password,
            )
        )
        company = response.company_id
        assert company
        if workers:
            for worker in workers:
                self.company_manager.add_worker_to_company(company, worker)
        if not confirmed:
            return company
        self.company_repository.confirm_company(company, self.datetime_service.now())
        return company


@dataclass
class AccountGenerator:
    account_repository: AccountRepository

    def create_account(self, account_type: AccountTypes = AccountTypes.a) -> Account:
        return self.account_repository.create_account(account_type)


class EmailGenerator:
    def get_random_email(self):
        return str(uuid4()) + "@cp.org"


@dataclass
class PlanGenerator:
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    request_cooperation: RequestCooperation
    accept_cooperation: AcceptCooperation
    draft_repository: PlanDraftRepository
    create_plan_draft_use_case: CreatePlanDraft
    file_plan_with_accounting: FilePlanWithAccounting
    approve_plan_use_case: ApprovePlanUseCase

    def create_plan(
        self,
        *,
        amount: int = 100,
        approved: bool = True,
        costs: Optional[ProductionCosts] = None,
        description="Beschreibung für Produkt A.",
        is_public_service: bool = False,
        planner: Optional[UUID] = None,
        product_name: str = "Produkt A",
        production_unit: str = "500 Gramm",
        timeframe: Optional[int] = None,
        requested_cooperation: Optional[Cooperation] = None,
        cooperation: Optional[Cooperation] = None,
        is_available: bool = True,
        hidden_by_user: bool = False,
    ) -> Plan:
        draft = self.draft_plan(
            planner=planner,
            costs=costs,
            product_name=product_name,
            production_unit=production_unit,
            amount=amount,
            description=description,
            timeframe=timeframe,
            is_public_service=is_public_service,
        )
        file_plan_response = self.file_plan_with_accounting.file_plan_with_accounting(
            request=FilePlanWithAccounting.Request(
                draft_id=draft.id, filing_company=draft.planner.id
            )
        )
        assert file_plan_response.plan_id
        assert file_plan_response.is_plan_successfully_filed
        if not approved:
            plan = (
                self.database_gateway.get_plans()
                .with_id(file_plan_response.plan_id)
                .first()
            )
            assert plan
            return plan
        response = self.approve_plan_use_case.approve_plan(
            ApprovePlanUseCase.Request(plan=file_plan_response.plan_id)
        )
        assert response.is_approved
        plan = (
            self.database_gateway.get_plans()
            .with_id(file_plan_response.plan_id)
            .first()
        )
        assert plan
        assert plan.is_approved
        if requested_cooperation:
            request_cooperation_response = self.request_cooperation(
                RequestCooperationRequest(
                    plan.planner, plan.id, requested_cooperation.id
                )
            )
            assert (
                not request_cooperation_response.is_rejected
            ), f"Cooperation request failed: {request_cooperation_response}"
        if cooperation:
            self.request_cooperation(
                RequestCooperationRequest(plan.planner, plan.id, cooperation.id)
            )
            self.accept_cooperation(
                AcceptCooperationRequest(
                    cooperation.coordinator.id, plan.id, cooperation.id
                )
            )
        selected_plan = self.database_gateway.get_plans().with_id(
            file_plan_response.plan_id
        )
        update = selected_plan.update()
        if hidden_by_user:
            update = update.hide()
        if not is_available:
            update = update.toggle_product_availability()
        update.perform()
        plan = (
            self.database_gateway.get_plans()
            .with_id(file_plan_response.plan_id)
            .first()
        )
        assert plan
        return plan

    def draft_plan(
        self,
        planner: Optional[UUID] = None,
        timeframe: Optional[int] = None,
        costs: Optional[ProductionCosts] = None,
        is_public_service: Optional[bool] = None,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        production_unit: Optional[str] = None,
        amount: Optional[int] = None,
    ) -> PlanDraft:
        if amount is None:
            amount = 5
        if production_unit is None:
            production_unit = "test unit"
        if description is None:
            description = "Beschreibung für Produkt A."
        if is_public_service is None:
            is_public_service = False
        if product_name is None:
            product_name = "Produkt A."
        if costs is None:
            costs = ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
        if planner is None:
            planner = self.company_generator.create_company()
        if timeframe is None:
            timeframe = 14
        response = self.create_plan_draft_use_case(
            request=CreatePlanDraftRequest(
                costs=costs,
                product_name=product_name,
                production_unit=production_unit,
                production_amount=amount,
                description=description,
                timeframe_in_days=timeframe,
                is_public_service=is_public_service,
                planner=planner,
            )
        )
        assert not response.is_rejected
        assert response.draft_id
        draft = self.draft_repository.get_by_id(response.draft_id)
        assert draft
        return draft


@dataclass
class PurchaseGenerator:
    plan_generator: PlanGenerator
    company_generator: CompanyGenerator
    member_generator: MemberGenerator
    pay_means: pay_means_of_production.PayMeansOfProduction
    pay_product: pay_consumer_product.PayConsumerProduct

    def create_resource_purchase_by_company(
        self,
        *,
        buyer: Optional[UUID] = None,
        plan: Optional[UUID] = None,
        amount: int = 1,
    ) -> pay_means_of_production.PayMeansOfProductionResponse:
        if buyer is None:
            buyer = self.company_generator.create_company()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        request = pay_means_of_production.PayMeansOfProductionRequest(
            buyer=buyer,
            plan=plan,
            amount=amount,
            purpose=PurposesOfPurchases.raw_materials,
        )
        response = self.pay_means(request)
        assert (
            not response.is_rejected
        ), f"Could not create purchase, response was {response}"
        return response

    def create_purchase_by_member(
        self,
        buyer: Optional[UUID] = None,
        amount: int = 1,
        plan: Optional[UUID] = None,
    ) -> pay_consumer_product.PayConsumerProductResponse:
        if buyer is None:
            buyer = self.member_generator.create_member()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        request = pay_consumer_product.PayConsumerProductRequest(
            amount=amount,
            plan=plan,
            buyer=buyer,
        )
        response = self.pay_product.pay_consumer_product(request)
        assert (
            response.is_accepted
        ), f"Could not create member purchase. Response was {response}"
        return response


@dataclass
class TransactionGenerator:
    account_generator: AccountGenerator
    transaction_repository: TransactionRepository
    datetime_service: FakeDatetimeService

    def create_transaction(
        self,
        sending_account_type=AccountTypes.p,
        receiving_account_type=AccountTypes.prd,
        sending_account: Optional[UUID] = None,
        receiving_account: Optional[UUID] = None,
        amount_sent=None,
        amount_received=None,
        purpose=None,
        date=None,
    ) -> Transaction:
        if sending_account is None:
            sending_account = self.account_generator.create_account(
                account_type=sending_account_type
            ).id
        if receiving_account is None:
            receiving_account = self.account_generator.create_account(
                account_type=receiving_account_type
            ).id
        if amount_sent is None:
            amount_sent = Decimal(10)
        if amount_received is None:
            amount_received = Decimal(10)
        if purpose is None:
            purpose = "test purpose"
        if date is None:
            date = self.datetime_service.now_minus_one_day()
        return self.transaction_repository.create_transaction(
            date=date,
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )


@dataclass
class CooperationGenerator:
    cooperation_repository: CooperationRepository
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    company_repository: CompanyRepository

    def create_cooperation(
        self,
        name: Optional[str] = None,
        coordinator: Optional[Union[Company, UUID]] = None,
        plans: Optional[List[Plan]] = None,
    ) -> Cooperation:
        if name is None:
            name = "test name"
        if coordinator is None:
            coordinator = self.company_generator.create_company_entity()
        if isinstance(coordinator, UUID):
            coordinator = (
                self.company_repository.get_companies().with_id(coordinator).first()
            )
            assert coordinator
        cooperation = self.cooperation_repository.create_cooperation(
            self.datetime_service.now(),
            name=name,
            definition="test info",
            coordinator=coordinator,
        )
        if plans is not None:
            assert (
                self.database_gateway.get_plans()
                .with_id(*[plan.id for plan in plans])
                .update()
                .set_cooperation(cooperation.id)
                .perform()
            )
        return cooperation


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
