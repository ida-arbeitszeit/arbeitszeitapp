"""Data generators defined in this module *should* only interact with
use case objects.  Some of the classes in this module violate this
rule though. Feel free to change them so that they comply.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Optional, Union
from uuid import UUID, uuid4

from arbeitszeit import records
from arbeitszeit.interactors import confirm_member, get_coop_summary
from arbeitszeit.interactors.accept_cooperation import (
    AcceptCooperationInteractor,
    AcceptCooperationRequest,
)
from arbeitszeit.interactors.answer_company_work_invite import (
    AnswerCompanyWorkInviteInteractor,
    AnswerCompanyWorkInviteRequest,
)
from arbeitszeit.interactors.approve_plan import ApprovePlanInteractor
from arbeitszeit.interactors.confirm_company import ConfirmCompanyInteractor
from arbeitszeit.interactors.create_cooperation import (
    CreateCooperationInteractor,
    CreateCooperationRequest,
)
from arbeitszeit.interactors.create_plan_draft import CreatePlanDraft, Request
from arbeitszeit.interactors.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.interactors.hide_plan import HidePlanInteractor
from arbeitszeit.interactors.invite_worker_to_company import (
    InviteWorkerToCompanyInteractor,
)
from arbeitszeit.interactors.register_accountant import RegisterAccountantInteractor
from arbeitszeit.interactors.register_company import RegisterCompany
from arbeitszeit.interactors.register_member import RegisterMemberInteractor
from arbeitszeit.interactors.register_private_consumption import (
    RegisterPrivateConsumption,
    RegisterPrivateConsumptionRequest,
    RegisterPrivateConsumptionResponse,
)
from arbeitszeit.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionInteractor,
    RegisterProductiveConsumptionRequest,
    RegisterProductiveConsumptionResponse,
)
from arbeitszeit.interactors.reject_plan import RejectPlanInteractor
from arbeitszeit.interactors.request_cooperation import (
    RequestCooperationInteractor,
    RequestCooperationRequest,
)
from arbeitszeit.interactors.request_coordination_transfer import (
    RequestCoordinationTransferInteractor,
)
from arbeitszeit.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType
from tests.datetime_service import FakeDatetimeService


@dataclass
class MemberGenerator:
    email_generator: EmailGenerator
    register_member_interactor: RegisterMemberInteractor
    confirm_member_interactor: confirm_member.ConfirmMemberInteractor

    def create_member(
        self,
        *,
        email: Optional[str] = None,
        name: str = "test member name",
        password: str = "password",
        confirmed: bool = True,
    ) -> UUID:
        if email is None:
            email = self.email_generator.get_random_email()
        register_response = self.register_member_interactor.register_member(
            request=RegisterMemberInteractor.Request(
                email=email, name=name, password=password
            )
        )
        assert register_response.user_id
        if confirmed:
            confirm_response = self.confirm_member_interactor.confirm_member(
                confirm_member.ConfirmMemberInteractor.Request(
                    email_address=email,
                )
            )
            assert confirm_response.is_confirmed
        return register_response.user_id


@dataclass
class CompanyGenerator:
    email_generator: EmailGenerator
    datetime_service: FakeDatetimeService
    worker_affiliation_generator: WorkerAffiliationGenerator
    register_company_interactor: RegisterCompany
    confirm_company_interactor: ConfirmCompanyInteractor
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
        response = self.register_company_interactor.register_company(
            request=RegisterCompany.Request(
                name=name,
                email=email,
                password=password,
            )
        )
        company = response.company_id
        assert company
        if workers:
            self.worker_affiliation_generator.add_workers_to_company(company, workers)
        if not confirmed:
            return company
        confirm_response = self.confirm_company_interactor.confirm_company(
            request=ConfirmCompanyInteractor.Request(email_address=email)
        )
        assert confirm_response.is_confirmed
        return company


class EmailGenerator:
    def get_random_email(self) -> str:
        return str(uuid4()) + "@cp.org"


@dataclass
class PlanGenerator:
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    request_cooperation: RequestCooperationInteractor
    accept_cooperation: AcceptCooperationInteractor
    create_plan_draft_interactor: CreatePlanDraft
    file_plan_with_accounting: FilePlanWithAccounting
    approve_plan_interactor: ApprovePlanInteractor
    hide_plan: HidePlanInteractor
    get_coop_summary_interactor: get_coop_summary.GetCoopSummaryInteractor
    reject_plan_interactor: RejectPlanInteractor

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
        hidden_by_user: bool = False,
        rejected: bool = False,
    ) -> UUID:
        assert not (
            requested_cooperation and cooperation
        ), "You cannot request a new cooperation for a plan that already belongs to one."
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
        assert not (approved and rejected)
        if not approved and not rejected:
            return file_plan_response.plan_id
        if approved:
            response = self.approve_plan_interactor.approve_plan(
                ApprovePlanInteractor.Request(plan=file_plan_response.plan_id)
            )
            assert response.is_plan_approved
        if rejected:
            rejected_response = self.reject_plan_interactor.reject_plan(
                RejectPlanInteractor.Request(plan=file_plan_response.plan_id)
            )
            assert rejected_response.is_plan_rejected
        if requested_cooperation:
            self._request_cooperation(
                planner=planner,
                plan=file_plan_response.plan_id,
                cooperation=requested_cooperation,
            )
        if cooperation:
            self._add_plan_to_cooperation(
                planner=planner,
                plan_id=file_plan_response.plan_id,
                cooperation=cooperation,
            )
        if hidden_by_user:
            self.hide_plan.execute(plan_id=file_plan_response.plan_id)
        return file_plan_response.plan_id

    def _add_plan_to_cooperation(
        self,
        planner: UUID,
        plan_id: UUID,
        cooperation: UUID,
    ) -> None:
        self._request_cooperation(
            planner=planner,
            plan=plan_id,
            cooperation=cooperation,
        )
        coordinator = self._get_cooperation_coordinator(cooperation, planner)
        self._accept_cooperation(
            coordinator=coordinator,
            plan=plan_id,
            cooperation=cooperation,
        )

    def _request_cooperation(
        self,
        planner: UUID,
        plan: UUID,
        cooperation: UUID,
    ) -> None:
        request = RequestCooperationRequest(
            requester_id=planner, plan_id=plan, cooperation_id=cooperation
        )
        response = self.request_cooperation.execute(request)
        if response.is_rejected:
            assert response.rejection_reason
            raise response.rejection_reason

    def _accept_cooperation(
        self,
        coordinator: UUID,
        plan: UUID,
        cooperation: UUID,
    ) -> None:
        request = AcceptCooperationRequest(
            requester_id=coordinator, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation.execute(request)
        if response.is_rejected:
            assert response.rejection_reason
            raise response.rejection_reason

    def _get_cooperation_coordinator(self, cooperation: UUID, planner: UUID) -> UUID:
        request = get_coop_summary.GetCoopSummaryRequest(
            requester_id=planner, coop_id=cooperation
        )
        response = self.get_coop_summary_interactor.execute(request)
        assert response
        return response.current_coordinator

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
        response = self.create_plan_draft_interactor.create_draft(
            request=Request(
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
        assert not response.is_rejected, f"Could not create draft: {response}"
        assert response.draft_id
        return response.draft_id

    def create_plan_record(
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
        hidden_by_user: bool = False,
    ) -> records.Plan:
        # Don't use this method. It is only here for legacy reasons.
        plan_id = self.create_plan(
            amount=amount,
            approved=approved,
            costs=costs,
            description=description,
            is_public_service=is_public_service,
            planner=planner,
            product_name=product_name,
            production_unit=production_unit,
            timeframe=timeframe,
            requested_cooperation=requested_cooperation,
            cooperation=cooperation,
            hidden_by_user=hidden_by_user,
        )
        plan = self.database_gateway.get_plans().with_id(plan_id).first()
        assert plan
        return plan


@dataclass
class ConsumptionGenerator:
    plan_generator: PlanGenerator
    company_generator: CompanyGenerator
    member_generator: MemberGenerator
    register_productive_consumption: RegisterProductiveConsumptionInteractor
    register_private_consumption_interactor: RegisterPrivateConsumption

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
            plan = self.plan_generator.create_plan()
        request = RegisterProductiveConsumptionRequest(
            consumer=consumer,
            plan=plan,
            amount=amount,
            consumption_type=consumption_type,
        )
        response = self.register_productive_consumption.execute(request)
        if response.is_rejected:
            assert response.rejection_reason
            raise response.rejection_reason
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
            plan = self.plan_generator.create_plan()
        request = RegisterPrivateConsumptionRequest(
            amount=amount,
            plan=plan,
            consumer=consumer,
        )
        response = (
            self.register_private_consumption_interactor.register_private_consumption(
                request
            )
        )
        if not response.is_accepted:
            assert response.rejection_reason
            raise response.rejection_reason
        return response


@dataclass
class TransferGenerator:
    datetime_service: FakeDatetimeService
    database_gateway: DatabaseGateway

    def create_transfer(
        self,
        date: Optional[datetime] = None,
        debit_account: Optional[UUID] = None,
        credit_account: Optional[UUID] = None,
        value: Optional[Decimal] = None,
        type: Optional[TransferType] = None,
    ) -> records.Transfer:
        if date is None:
            date = self.datetime_service.now()
        if debit_account is None:
            debit_account = self.database_gateway.create_account().id
        if credit_account is None:
            credit_account = self.database_gateway.create_account().id
        if value is None:
            value = Decimal(10)
        if type is None:
            type = TransferType.credit_p
        return self.database_gateway.create_transfer(
            date=date,
            debit_account=debit_account,
            credit_account=credit_account,
            value=value,
            type=type,
        )


@dataclass
class CooperationGenerator:
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    create_cooperation_interactor: CreateCooperationInteractor
    request_cooperation_interactor: RequestCooperationInteractor
    accept_cooperation_interactor: AcceptCooperationInteractor

    def create_cooperation(
        self,
        name: Optional[str] = None,
        coordinator: Optional[Union[records.Company, UUID]] = None,
        plans: Optional[List[UUID]] = None,
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
        uc_response = self.create_cooperation_interactor.execute(uc_request)
        assert not uc_response.is_rejected
        cooperation_id = uc_response.cooperation_id
        assert cooperation_id
        if plans is not None:
            for plan in plans:
                planner = self._get_planner(plan)
                self._add_plan_to_cooperation(
                    planner=planner,
                    plan=plan,
                    cooperation=cooperation_id,
                    coordinator=coordinator,
                )
        cooperation_record = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation_record
        return cooperation_record.id

    def _get_planner(self, plan: UUID) -> UUID:
        plan_record = self.database_gateway.get_plans().with_id(plan).first()
        assert plan_record
        return plan_record.planner

    def _add_plan_to_cooperation(
        self,
        planner: UUID,
        plan: UUID,
        cooperation: UUID,
        coordinator: UUID,
    ) -> None:
        request = RequestCooperationRequest(
            requester_id=planner, plan_id=plan, cooperation_id=cooperation
        )
        request_response = self.request_cooperation_interactor.execute(request)
        if request_response.is_rejected:
            assert request_response.rejection_reason
            raise request_response.rejection_reason
        accept_response = self.accept_cooperation_interactor.execute(
            AcceptCooperationRequest(coordinator, plan, cooperation)
        )
        if accept_response.is_rejected:
            assert accept_response.rejection_reason
            raise accept_response.rejection_reason


@dataclass
class CoordinationTenureGenerator:
    datetime_service: FakeDatetimeService
    company_generator: CompanyGenerator
    database_gateway: DatabaseGateway
    create_cooperation_interactor: CreateCooperationInteractor

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
        uc_response = self.create_cooperation_interactor.execute(uc_request)
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
    request_transfer_interactor: RequestCoordinationTransferInteractor

    def create_coordination_transfer_request(
        self,
        requester: Optional[UUID] = None,
        cooperation: Optional[UUID] = None,
        candidate: Optional[UUID] = None,
    ) -> UUID:
        if requester is None:
            requester = self.company_generator.create_company()
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation()
        if candidate is None:
            candidate = self.company_generator.create_company()
        request_response = self.request_transfer_interactor.request_transfer(
            RequestCoordinationTransferInteractor.Request(
                requester=requester,
                cooperation=cooperation,
                candidate=candidate,
            )
        )
        assert not request_response.is_rejected, request_response.rejection_reason
        assert request_response.transfer_request
        transfer_request = request_response.transfer_request
        return transfer_request


@dataclass
class AccountantGenerator:
    invite_accountant_interactor: SendAccountantRegistrationTokenInteractor
    register_accountant_interactor: RegisterAccountantInteractor
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
        self.invite_accountant_interactor.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenInteractor.Request(
                email=email_address
            )
        )
        response = self.register_accountant_interactor.register_accountant(
            request=RegisterAccountantInteractor.Request(
                name=name,
                email=email_address,
                password=password,
            )
        )
        assert response.is_accepted
        assert response.user_id
        return response.user_id


@dataclass
class WorkerAffiliationGenerator:
    invite_worker_interactor: InviteWorkerToCompanyInteractor
    answer_invite_interactor: AnswerCompanyWorkInviteInteractor

    def add_workers_to_company(self, company: UUID, workers=Iterable[UUID]) -> None:
        for worker in workers:
            self._add_worker_to_company(company, worker)

    def _add_worker_to_company(self, company: UUID, worker: UUID) -> None:
        response = self.invite_worker_interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(company=company, worker=worker)
        )
        if response.rejection_reason:
            raise ValueError(
                f"Could not invite worker {worker} to company {company}: {response.rejection_reason}"
            )
        if response.invite_id:
            answer_response = self.answer_invite_interactor.execute(
                AnswerCompanyWorkInviteRequest(
                    is_accepted=True,
                    invite_id=response.invite_id,
                    user=worker,
                )
            )
            if answer_response.failure_reason:
                raise ValueError(
                    f"Could not accept invite for worker {worker}: {answer_response.failure_reason}"
                )
