"""Data generators defined in this module *should* only interact with
use case objects.  Some of the classes in this module violate this
rule though. Feel free to change them so that they comply.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Optional, Union
from uuid import UUID, uuid4

from arbeitszeit import records
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.use_cases import confirm_member
from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase
from arbeitszeit.use_cases.create_cooperation import (
    CreateCooperation,
    CreateCooperationRequest,
)
from arbeitszeit.use_cases.create_plan_draft import (
    CreatePlanDraft,
    CreatePlanDraftRequest,
)
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumption,
    RegisterPrivateConsumptionRequest,
    RegisterPrivateConsumptionResponse,
)
from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
    RegisterProductiveConsumptionRequest,
    RegisterProductiveConsumptionResponse,
)
from arbeitszeit.use_cases.request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
)
from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase,
)
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
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

    def create_member_record(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        password: str = "password",
        confirmed: bool = True,
    ) -> records.Member:
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
        member = self.create_member_record(
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

    def create_company_record(
        self,
        *,
        email: Optional[str] = None,
        name: str = "Company Name",
        password: str = "password",
        workers: Optional[Iterable[UUID]] = None,
    ) -> records.Company:
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

    def create_account(self) -> records.Account:
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
        costs: Optional[records.ProductionCosts] = None,
        description="Beschreibung für Produkt A.",
        is_public_service: bool = False,
        planner: Optional[UUID] = None,
        product_name: str = "Produkt A",
        production_unit: str = "500 Gramm",
        timeframe: Optional[int] = None,
        requested_cooperation: Optional[UUID] = None,
        cooperation: Optional[UUID] = None,
        is_available: bool = True,
        hidden_by_user: bool = False,
    ) -> records.Plan:
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
                RequestCooperationRequest(plan.planner, plan.id, requested_cooperation)
            )
            assert (
                not request_cooperation_response.is_rejected
            ), f"Cooperation request failed: {request_cooperation_response}"
        if cooperation:
            coop_and_coordinator = (
                self.database_gateway.get_cooperations()
                .with_id(cooperation)
                .joined_with_current_coordinator()
                .first()
            )
            assert coop_and_coordinator
            _, coordinator = coop_and_coordinator
            self.request_cooperation(
                RequestCooperationRequest(plan.planner, plan.id, cooperation)
            )
            self.accept_cooperation(
                AcceptCooperationRequest(coordinator.id, plan.id, cooperation)
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
        costs: Optional[records.ProductionCosts] = None,
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
            costs = records.ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
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
class ConsumptionGenerator:
    plan_generator: PlanGenerator
    company_generator: CompanyGenerator
    member_generator: MemberGenerator
    register_productive_consumption: RegisterProductiveConsumption
    register_private_consumption_use_case: RegisterPrivateConsumption

    def create_resource_consumption_by_company(
        self,
        *,
        consumer: Optional[UUID] = None,
        plan: Optional[UUID] = None,
        amount: int = 1,
    ) -> RegisterProductiveConsumptionResponse:
        return self._create_productive_consumption(
            consumption_type=records.ConsumptionType.raw_materials,
            consumer=consumer,
            plan=plan,
            amount=amount,
        )

    def create_fixed_means_consumption(
        self,
        *,
        consumer: Optional[UUID] = None,
        plan: Optional[UUID] = None,
        amount: int = 1,
    ) -> RegisterProductiveConsumptionResponse:
        return self._create_productive_consumption(
            consumption_type=records.ConsumptionType.means_of_prod,
            consumer=consumer,
            plan=plan,
            amount=amount,
        )

    def _create_productive_consumption(
        self,
        *,
        consumption_type: records.ConsumptionType,
        consumer: Optional[UUID] = None,
        plan: Optional[UUID] = None,
        amount: int = 1,
    ) -> RegisterProductiveConsumptionResponse:
        if consumer is None:
            consumer = self.company_generator.create_company()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        request = RegisterProductiveConsumptionRequest(
            consumer=consumer,
            plan=plan,
            amount=amount,
            consumption_type=consumption_type,
        )
        response = self.register_productive_consumption(request)
        assert (
            not response.is_rejected
        ), f"Could not create productive consumption, response was {response}"
        return response

    def create_private_consumption(
        self,
        consumer: Optional[UUID] = None,
        amount: int = 1,
        plan: Optional[UUID] = None,
    ) -> RegisterPrivateConsumptionResponse:
        if consumer is None:
            consumer = self.member_generator.create_member()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        request = RegisterPrivateConsumptionRequest(
            amount=amount,
            plan=plan,
            consumer=consumer,
        )
        response = (
            self.register_private_consumption_use_case.register_private_consumption(
                request
            )
        )
        assert (
            response.is_accepted
        ), f"Could not create private consumption. Response was {response}"
        return response


@dataclass
class TransactionGenerator:
    account_generator: AccountGenerator
    datetime_service: FakeDatetimeService
    database_gateway: DatabaseGateway

    def create_transaction(
        self,
        sending_account: Optional[UUID] = None,
        receiving_account: Optional[UUID] = None,
        amount_sent=None,
        amount_received=None,
        purpose=None,
        date=None,
    ) -> records.Transaction:
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
    create_cooperation_use_case: CreateCooperation

    def create_cooperation(
        self,
        name: Optional[str] = None,
        coordinator: Optional[Union[records.Company, UUID]] = None,
        plans: Optional[List[records.Plan]] = None,
    ) -> UUID:
        if name is None:
            name = f"name_{uuid4()}"
        if coordinator is None:
            coordinator = self.company_generator.create_company_record()
        if isinstance(coordinator, records.Company):
            coordinator = coordinator.id
        uc_request = CreateCooperationRequest(
            coordinator_id=coordinator, name=name, definition="test info"
        )
        uc_response = self.create_cooperation_use_case(uc_request)
        assert not uc_response.is_rejected
        cooperation_id = uc_response.cooperation_id
        assert cooperation_id
        if plans is not None:
            assert (
                self.database_gateway.get_plans()
                .with_id(*[plan.id for plan in plans])
                .update()
                .set_cooperation(cooperation_id)
                .perform()
            )
        cooperation_record = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation_record
        return cooperation_record.id


@dataclass
class CoordinationTenureGenerator:
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    create_cooperation_use_case: CreateCooperation

    def create_coordination_tenure(
        self, cooperation: Optional[UUID] = None, coordinator: Optional[UUID] = None
    ) -> UUID:
        if coordinator is None:
            coordinator = self.company_generator.create_company()
        if cooperation is None:
            cooperation = self._create_coop(coordinator=coordinator)
        tenure = self._create_tenure(cooperation=cooperation, coordinator=coordinator)
        return tenure

    def _create_coop(self, coordinator: UUID) -> UUID:
        uc_request = CreateCooperationRequest(
            coordinator_id=coordinator, name=f"name_{uuid4()}", definition="test info"
        )
        uc_response = self.create_cooperation_use_case(uc_request)
        assert uc_response.cooperation_id
        cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(uc_response.cooperation_id)
            .first()
        )
        assert cooperation
        return cooperation.id

    def _create_tenure(self, cooperation: UUID, coordinator: UUID) -> UUID:
        tenure = self.database_gateway.create_coordination_tenure(
            company=coordinator,
            cooperation=cooperation,
            start_date=self.datetime_service.now(),
        )
        return tenure.id


@dataclass
class CoordinationTransferRequestGenerator:
    cooperation_generator: CooperationGenerator
    company_generator: CompanyGenerator
    request_transfer_use_case: RequestCoordinationTransferUseCase

    def create_coordination_transfer_request(
        self,
        current_user: Optional[UUID] = None,
        cooperation: Optional[UUID] = None,
        candidate: Optional[UUID] = None,
    ) -> UUID:
        if current_user is None:
            current_user = self.company_generator.create_company()
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation()
        if candidate is None:
            candidate = self.company_generator.create_company()
        request_response = self.request_transfer_use_case.request_transfer(
            RequestCoordinationTransferUseCase.Request(
                current_user=current_user,
                cooperation=cooperation,
                candidate=candidate,
            )
        )
        assert not request_response.is_rejected
        assert request_response.transfer_request
        transfer_request = request_response.transfer_request
        return transfer_request


@dataclass
class AccountantGenerator:
    invite_accountant_use_case: SendAccountantRegistrationTokenUseCase
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
