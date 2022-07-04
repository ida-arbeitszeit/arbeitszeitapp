from functools import wraps
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from injector import (
    Binder,
    CallableProvider,
    ClassProvider,
    Injector,
    InstanceProvider,
    Module,
    inject,
    provider,
    singleton,
)

from arbeitszeit import entities
from arbeitszeit import repositories as interfaces
from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.token import InvitationTokenValidator, TokenDeliverer, TokenService
from arbeitszeit.use_cases import GetCompanySummary
from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
from arbeitszeit_flask.control_thresholds import ControlThresholdsFlask
from arbeitszeit_flask.database import get_social_accounting
from arbeitszeit_flask.database.repositories import (
    AccountantRepository,
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    CooperationRepository,
    MemberRepository,
    PlanCooperationRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    UserAddressBookImpl,
    WorkerInviteRepository,
)
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import db
from arbeitszeit_flask.flask_colors import FlaskColors
from arbeitszeit_flask.flask_plotter import FlaskPlotter
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.language_repository import LanguageRepositoryImpl
from arbeitszeit_flask.mail_service import (
    FlaskEmailConfiguration,
    FlaskTokenDeliverer,
    MailService,
    get_mail_service,
)
from arbeitszeit_flask.notifications import FlaskFlashNotifier
from arbeitszeit_flask.template import (
    AnonymousUserTemplateRenderer,
    CompanyTemplateIndex,
    FlaskTemplateRenderer,
    MemberRegistrationEmailTemplateImpl,
    MemberTemplateIndex,
    TemplateIndex,
    TemplateRenderer,
    UserTemplateRenderer,
)
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.translator import FlaskTranslator
from arbeitszeit_flask.url_index import (
    CompanyUrlIndex,
    FlaskPlotsUrlIndex,
    MemberUrlIndex,
)
from arbeitszeit_flask.views import Http404View
from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInviteController
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.controllers.list_workers_controller import ListWorkersController
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from arbeitszeit_web.controllers.send_work_certificates_to_worker_controller import (
    SendWorkCertificatesToWorkerController,
)
from arbeitszeit_web.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from arbeitszeit_web.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from arbeitszeit_web.email import EmailConfiguration, UserAddressBook
from arbeitszeit_web.formatters.plan_summary_formatter import PlanSummaryFormatter
from arbeitszeit_web.get_prefilled_draft_data import PrefilledDraftDataController
from arbeitszeit_web.invite_worker_to_company import InviteWorkerToCompanyController
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)
from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailTemplate,
)
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)
from arbeitszeit_web.request_cooperation import RequestCooperationController
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    AnswerCompanyWorkInviteUrlIndex,
    CompanySummaryUrlIndex,
    ConfirmationUrlIndex,
    CoopSummaryUrlIndex,
    EndCoopUrlIndex,
    HidePlanUrlIndex,
    InviteUrlIndex,
    PlanSummaryUrlIndex,
    PlotsUrlIndex,
    RenewPlanUrlIndex,
    RequestCoopUrlIndex,
    TogglePlanAvailabilityUrlIndex,
)

from .presenters import CompanyPresenterModule, MemberPresenterModule, PresenterModule
from .views import ViewsModule

__all__ = [
    "ViewsModule",
]


class MemberModule(MemberPresenterModule):
    @provider
    def provide_confirmation_url_index(
        self, member_index: MemberUrlIndex
    ) -> ConfirmationUrlIndex:
        return member_index

    @provider
    def provide_plan_summary_url_index(
        self, member_index: MemberUrlIndex
    ) -> PlanSummaryUrlIndex:
        return member_index

    @provider
    def provide_coop_summary_url_index(
        self, member_index: MemberUrlIndex
    ) -> CoopSummaryUrlIndex:
        return member_index

    @provider
    def provide_request_coop_url_index(
        self, member_index: MemberUrlIndex
    ) -> RequestCoopUrlIndex:
        return member_index

    @provider
    def provide_end_coop_url_index(
        self, member_index: MemberUrlIndex
    ) -> EndCoopUrlIndex:
        return member_index

    @provider
    def provide_company_url_index(
        self, member_index: MemberUrlIndex
    ) -> CompanySummaryUrlIndex:
        return member_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return MemberTemplateIndex()

    @provider
    def provide_invite_url_index(self, index: MemberUrlIndex) -> InviteUrlIndex:
        return index

    @provider
    def provide_answer_company_work_invite_url_index(
        self, url_index: MemberUrlIndex
    ) -> AnswerCompanyWorkInviteUrlIndex:
        return url_index


class CompanyModule(CompanyPresenterModule):
    @provider
    def provide_confirmation_url_index(
        self, company_index: CompanyUrlIndex
    ) -> ConfirmationUrlIndex:
        return company_index

    @provider
    def provide_plan_summary_url_index(
        self, company_index: CompanyUrlIndex
    ) -> PlanSummaryUrlIndex:
        return company_index

    @provider
    def provide_coop_summary_url_index(
        self, company_index: CompanyUrlIndex
    ) -> CoopSummaryUrlIndex:
        return company_index

    @provider
    def provide_toggle_plan_availability_url_index(
        self, company_index: CompanyUrlIndex
    ) -> TogglePlanAvailabilityUrlIndex:
        return company_index

    @provider
    def provide_renew_plan_url_index(
        self, company_index: CompanyUrlIndex
    ) -> RenewPlanUrlIndex:
        return company_index

    @provider
    def provide_hide_plan_url_index(
        self, company_index: CompanyUrlIndex
    ) -> HidePlanUrlIndex:
        return company_index

    @provider
    def provide_request_coop_url_index(
        self, company_index: CompanyUrlIndex
    ) -> RequestCoopUrlIndex:
        return company_index

    @provider
    def provide_end_coop_url_index(
        self, company_index: CompanyUrlIndex
    ) -> EndCoopUrlIndex:
        return company_index

    @provider
    def provide_company_url_index(
        self, company_index: CompanyUrlIndex
    ) -> CompanySummaryUrlIndex:
        return company_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return CompanyTemplateIndex()

    @provider
    def provide_end_cooperation_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> EndCooperationController:
        return EndCooperationController(session, request)

    @provider
    def provide_send_work_certificates_to_worker_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> SendWorkCertificatesToWorkerController:
        return SendWorkCertificatesToWorkerController(session, request)

    @provider
    def provide_pay_means_of_production_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> PayMeansOfProductionController:
        return PayMeansOfProductionController(session, request)

    @provider
    def provide_invite_url_index(self, index: CompanyUrlIndex) -> InviteUrlIndex:
        return index

    @provider
    def provide_answer_company_work_invite_url_index(
        self, url_index: CompanyUrlIndex
    ) -> AnswerCompanyWorkInviteUrlIndex:
        return url_index

    @provider
    def provide_prefilled_draft_data_controller(
        self, session: Session
    ) -> PrefilledDraftDataController:
        return PrefilledDraftDataController(session=session)


class FlaskModule(PresenterModule):
    @provider
    def provide_invitation_token_validator(
        self, validator: FlaskTokenService
    ) -> InvitationTokenValidator:
        return validator

    @provider
    def provide_flask_session(
        self,
        member_repository: MemberRepository,
        company_repository: CompanyRepository,
        accountant_repository: AccountantRepository,
    ) -> FlaskSession:
        return FlaskSession(
            member_repository, company_repository, accountant_repository
        )

    @provider
    def provide_plots_url_index(
        self, flask_plots_url_index: FlaskPlotsUrlIndex
    ) -> PlotsUrlIndex:
        return flask_plots_url_index

    @provider
    def provide_member_registration_email_template(
        self,
    ) -> RegistrationEmailTemplate:
        return MemberRegistrationEmailTemplateImpl()

    @provider
    def provide_get_company_summary(
        self,
        company_repository: interfaces.CompanyRepository,
        plan_repository: interfaces.PlanRepository,
        account_repository: interfaces.AccountRepository,
        transaction_repository: interfaces.TransactionRepository,
        social_accounting: entities.SocialAccounting,
    ) -> GetCompanySummary:
        return GetCompanySummary(
            company_repository,
            plan_repository,
            account_repository,
            transaction_repository,
            social_accounting,
        )

    @provider
    def provide_language_repository(
        self, language_repository: LanguageRepositoryImpl
    ) -> interfaces.LanguageRepository:
        return language_repository

    @provider
    def provide_language_service(
        self, language_repository_impl: LanguageRepositoryImpl
    ) -> LanguageService:
        return language_repository_impl

    @provider
    def provide_list_workers_controller(
        self, session: Session
    ) -> ListWorkersController:
        return ListWorkersController(session=session)

    @provider
    def provide_show_company_work_invite_details_controller(
        self,
        session: Session,
    ) -> ShowCompanyWorkInviteDetailsController:
        return ShowCompanyWorkInviteDetailsController(
            session=session,
        )

    @provider
    def provide_answer_company_work_invite_controller(
        self, session: Session
    ) -> AnswerCompanyWorkInviteController:
        return AnswerCompanyWorkInviteController(session)

    @provider
    def provide_email_configuration(self) -> EmailConfiguration:
        return FlaskEmailConfiguration()

    @provider
    def provide_token_deliverer(
        self, mail_service: MailService, presenter: SendConfirmationEmailPresenter
    ) -> TokenDeliverer:
        return FlaskTokenDeliverer(mail_service=mail_service, presenter=presenter)

    @provider
    def provide_http_404_view(
        self, template_renderer: TemplateRenderer, template_index: TemplateIndex
    ) -> Http404View:
        return Http404View(
            template_index=template_index, template_renderer=template_renderer
        )

    @provider
    def provide_plan_summary_service(
        self,
        coop_url_index: CoopSummaryUrlIndex,
        company_url_index: CompanySummaryUrlIndex,
        translator: Translator,
        datetime_service: RealtimeDatetimeService,
    ) -> PlanSummaryFormatter:
        return PlanSummaryFormatter(
            coop_url_index, company_url_index, translator, datetime_service
        )

    @provider
    def provide_transaction_repository(
        self, instance: TransactionRepository
    ) -> interfaces.TransactionRepository:
        return instance

    @provider
    def provide_accountant_repository(
        self, instance: AccountantRepository
    ) -> interfaces.AccountantRepository:
        return instance

    @provider
    def provide_template_renderer(self) -> TemplateRenderer:
        return FlaskTemplateRenderer()

    @provider
    def provide_invite_worker_to_company_controller(
        self, session: Session
    ) -> InviteWorkerToCompanyController:
        return InviteWorkerToCompanyController(session)

    @provider
    def provide_user_template_renderer(
        self, flask_template_renderer: FlaskTemplateRenderer
    ) -> UserTemplateRenderer:
        return UserTemplateRenderer(flask_template_renderer)

    @provider
    def provide_anonymous_user_template_renderer(
        self,
        inner_renderer: TemplateRenderer,
        list_languages_user_case: ListAvailableLanguagesUseCase,
        list_languages_presenter: ListAvailableLanguagesPresenter,
    ) -> AnonymousUserTemplateRenderer:
        return AnonymousUserTemplateRenderer(
            inner_renderer=inner_renderer,
            list_languages_use_case=list_languages_user_case,
            list_languages_presenter=list_languages_presenter,
        )

    @provider
    def provide_request_cooperation_controller(
        self, session: Session, translator: Translator
    ) -> RequestCooperationController:
        return RequestCooperationController(session, translator)

    @provider
    def provide_session(self, flask_session: FlaskSession) -> Session:
        return flask_session

    @provider
    def provide_notifier(self) -> Notifier:
        return FlaskFlashNotifier()

    @singleton
    @provider
    def provide_mail_service(self) -> MailService:
        return get_mail_service()

    @provider
    def provide_translator(self) -> Translator:
        return FlaskTranslator()

    @provider
    def provide_plotter(self) -> Plotter:
        return FlaskPlotter()

    @provider
    def provide_colors(self) -> Colors:
        return FlaskColors()

    @provider
    def provide_show_my_accounts_controller(
        self, session: FlaskSession
    ) -> ShowMyAccountsController:
        return ShowMyAccountsController(session)

    @provider
    def provide_show_my_accounts_use_case(
        self,
        company_repository: CompanyRepository,
        account_repository: AccountRepository,
    ) -> ShowMyAccounts:
        return ShowMyAccounts(company_repository, account_repository)

    @provider
    def provide_list_available_languages_use_case(
        self, language_repository: interfaces.LanguageRepository
    ) -> ListAvailableLanguagesUseCase:
        return ListAvailableLanguagesUseCase(language_repository=language_repository)

    @provider
    def provide_log_in_member_use_case(
        self, member_repository: MemberRepository
    ) -> LogInMemberUseCase:
        return LogInMemberUseCase(
            member_repository=member_repository,
        )

    @provider
    def provide_control_thresholds(
        self, control_thresholds: ControlThresholdsFlask
    ) -> ControlThresholds:
        return control_thresholds

    @provider
    def provide_log_in_company_use_case(
        self, company_repository: CompanyRepository
    ) -> LogInCompanyUseCase:
        return LogInCompanyUseCase(
            company_repository=company_repository,
        )

    def configure(self, binder: Binder) -> None:
        binder.bind(
            interfaces.CompanyWorkerRepository,  # type: ignore
            to=ClassProvider(CompanyWorkerRepository),
        )
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            entities.SocialAccounting,
            to=CallableProvider(get_social_accounting),
        )
        binder.bind(
            interfaces.AccountRepository,  # type: ignore
            to=ClassProvider(AccountRepository),
        )
        binder.bind(
            interfaces.MemberRepository,  # type: ignore
            to=ClassProvider(MemberRepository),
        )
        binder.bind(
            interfaces.CompanyRepository,  # type: ignore
            to=ClassProvider(CompanyRepository),
        )
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            interfaces.PlanRepository,  # type: ignore
            to=ClassProvider(PlanRepository),
        )
        binder.bind(
            interfaces.AccountOwnerRepository,  # type: ignore
            to=ClassProvider(AccountOwnerRepository),
        )
        binder.bind(
            interfaces.PlanDraftRepository,  # type: ignore
            to=ClassProvider(PlanDraftRepository),
        )
        binder.bind(
            DatetimeService,  # type: ignore
            to=ClassProvider(RealtimeDatetimeService),
        )
        binder.bind(
            interfaces.WorkerInviteRepository,  # type: ignore
            to=ClassProvider(WorkerInviteRepository),
        )
        binder.bind(
            SQLAlchemy,
            to=InstanceProvider(db),
        )
        binder.bind(
            interfaces.CooperationRepository,  # type: ignore
            to=ClassProvider(CooperationRepository),
        )
        binder.bind(
            interfaces.PlanCooperationRepository,  # type: ignore
            to=ClassProvider(PlanCooperationRepository),
        )
        binder.bind(TokenService, to=ClassProvider(FlaskTokenService))  # type: ignore
        binder.bind(UserAddressBook, to=ClassProvider(inject(UserAddressBookImpl)))  # type: ignore


class with_injection:
    def __init__(self, modules: Optional[List[Module]] = None) -> None:
        self._modules = modules if modules is not None else []
        all_modules: List[Module] = []
        all_modules.append(FlaskModule())
        all_modules.append(ViewsModule())
        all_modules += self._modules
        self._injector = Injector(all_modules)

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self._injector.call_with_injection(
                inject(original_function), args=args, kwargs=kwargs
            )

        return wrapped_function

    @property
    def injector(self) -> Injector:
        return self._injector
