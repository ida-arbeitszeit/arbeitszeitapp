"""The classes in this module should only provide instances of
entities. Never should these entities automatically be added to a
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Optional, Union
from uuid import UUID, uuid4

from arbeitszeit import entities
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.use_cases import (
    confirm_member,
    pay_consumer_product,
    pay_means_of_production,
)
from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase
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
    database: DatabaseGateway
    datetime_service: FakeDatetimeService
    register_member_use_case: RegisterMemberUseCase
    confirm_member_use_case: confirm_member.ConfirmMemberUseCase
    password_hasher: PasswordHasher

    def create_member_entity(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        password: str = "password",
        confirmed: bool = True,
    ) -> entities.Member:
        if email is None:
            email = self.email_generator.get_random_email()
        register_response = self.register_member_use_case.register_member(
            request=RegisterMemberUseCase.Request(
                email=email, name=name, password=password
            )
        )
        assert register_response.user_id
        if confirmed:
            confirm_response = self.confirm_member_use_case.confirm_member(
                confirm_member.ConfirmMemberUseCase.Request(
                    email_address=email,
                )
            )
            assert confirm_response.is_confirmed
        member = self.database.get_members().with_id(register_response.user_id).first()
        assert member
        return member

    def create_member(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        password: str = "password",
        confirmed: bool = True,
    ) -> UUID:
        member = self.create_member_entity(
            email=email,
            name=name,
            password=password,
            confirmed=confirmed,
        )
        return member.id


@dataclass
class CompanyGenerator:
    account_generator: AccountGenerator
    email_generator: EmailGenerator
    datetime_service: FakeDatetimeService
    company_manager: CompanyManager
    register_company_use_case: RegisterCompany
    confirm_company_use_case: ConfirmCompanyUseCase
    password_hasher: PasswordHasher
    database: DatabaseGateway

    def create_company_entity(
        self,
        *,
        email: Optional[str] = None,
        name: str = "Company Name",
        password: str = "password",
        workers: Optional[Iterable[UUID]] = None,
    ) -> entities.Company:
        company_id = self.create_company(
            email=email, confirmed=True, name=name, workers=workers, password=password
        )
        company = self.database.get_companies().with_id(company_id).first()
        assert company
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
        confirm_response = self.confirm_company_use_case.confirm_company(
            request=ConfirmCompanyUseCase.Request(email_address=email)
        )
        assert confirm_response.is_confirmed
        return company


@dataclass
class AccountGenerator:
    database: DatabaseGateway

    def create_account(self) -> entities.Account:
        return self.database.create_account()


class EmailGenerator:
    def get_random_email(self) -> str:
        return str(uuid4()) + "@cp.org"


@dataclass
class PlanGenerator:
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    request_cooperation: RequestCooperation
    accept_cooperation: AcceptCooperation
    create_plan_draft_use_case: CreatePlanDraft
    file_plan_with_accounting: FilePlanWithAccounting
    approve_plan_use_case: ApprovePlanUseCase

    def create_plan(
        self,
        *,
        amount: int = 100,
        approved: bool = True,
        costs: Optional[entities.ProductionCosts] = None,
        description="Beschreibung für Produkt A.",
        is_public_service: bool = False,
        planner: Optional[UUID] = None,
        product_name: str = "Produkt A",
        production_unit: str = "500 Gramm",
        timeframe: Optional[int] = None,
        requested_cooperation: Optional[entities.Cooperation] = None,
        cooperation: Optional[entities.Cooperation] = None,
        is_available: bool = True,
        hidden_by_user: bool = False,
    ) -> entities.Plan:
        if planner is None:
            planner = self.company_generator.create_company()
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
                draft_id=draft, filing_company=planner
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
                    cooperation.coordinator, plan.id, cooperation.id
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
        costs: Optional[entities.ProductionCosts] = None,
        is_public_service: Optional[bool] = None,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        production_unit: Optional[str] = None,
        amount: Optional[int] = None,
    ) -> UUID:
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
            costs = entities.ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
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
        return response.draft_id


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
        return self._create_company_purchase(
            purpose=entities.PurposesOfPurchases.raw_materials,
            buyer=buyer,
            plan=plan,
            amount=amount,
        )

    def create_fixed_means_purchase(
        self,
        *,
        buyer: Optional[UUID] = None,
        plan: Optional[UUID] = None,
        amount: int = 1,
    ) -> pay_means_of_production.PayMeansOfProductionResponse:
        return self._create_company_purchase(
            purpose=entities.PurposesOfPurchases.means_of_prod,
            buyer=buyer,
            plan=plan,
            amount=amount,
        )

    def _create_company_purchase(
        self,
        *,
        purpose: entities.PurposesOfPurchases,
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
            purpose=purpose,
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
    datetime_service: FakeDatetimeService
    database_gateway: DatabaseGateway

    def create_transaction(
        self,
        sending_account_type=entities.AccountTypes.p,
        receiving_account_type=entities.AccountTypes.prd,
        sending_account: Optional[UUID] = None,
        receiving_account: Optional[UUID] = None,
        amount_sent=None,
        amount_received=None,
        purpose=None,
        date=None,
    ) -> entities.Transaction:
        if sending_account is None:
            sending_account = self.account_generator.create_account().id
        if receiving_account is None:
            receiving_account = self.account_generator.create_account().id
        if amount_sent is None:
            amount_sent = Decimal(10)
        if amount_received is None:
            amount_received = Decimal(10)
        if purpose is None:
            purpose = "test purpose"
        if date is None:
            date = self.datetime_service.now_minus_one_day()
        return self.database_gateway.create_transaction(
            date=date,
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )


@dataclass
class CooperationGenerator:
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway

    def create_cooperation(
        self,
        name: Optional[str] = None,
        coordinator: Optional[Union[entities.Company, UUID]] = None,
        plans: Optional[List[entities.Plan]] = None,
    ) -> entities.Cooperation:
        if name is None:
            name = "test name"
        if coordinator is None:
            coordinator = self.company_generator.create_company_entity()
        if isinstance(coordinator, entities.Company):
            coordinator = coordinator.id
        cooperation = self.database_gateway.create_cooperation(
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
        response = self.register_accountant_use_case.register_accountant(
            request=RegisterAccountantUseCase.Request(
                name=name,
                email=email_address,
                password=password,
            )
        )
        assert response.is_accepted
        assert response.user_id
        return response.user_id
