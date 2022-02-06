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
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.token import TokenDeliverer, TokenService
from arbeitszeit.use_cases import CheckForUnreadMessages, EndCooperation, ReadMessage
from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
from arbeitszeit_flask.database import get_social_accounting
from arbeitszeit_flask.database.repositories import (
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    CooperationRepository,
    MemberRepository,
    MessageRepository,
    PlanCooperationRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    WorkerInviteRepository,
)
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import db
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.mail_service import (
    FlaskEmailConfiguration,
    FlaskTokenDeliverer,
    MailService,
    get_mail_service,
)
from arbeitszeit_flask.notifications import FlaskFlashNotifier
from arbeitszeit_flask.template import (
    CompanyTemplateIndex,
    FlaskTemplateRenderer,
    MemberTemplateIndex,
    TemplateIndex,
    TemplateRenderer,
    UserTemplateRenderer,
)
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.url_index import CompanyUrlIndex, MemberUrlIndex
from arbeitszeit_flask.views import EndCooperationView, Http404View, ReadMessageView
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_web.check_for_unread_message import (
    CheckForUnreadMessagesController,
    CheckForUnreadMessagesPresenter,
)
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from arbeitszeit_web.email import EmailConfiguration
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from arbeitszeit_web.get_plan_summary_member import GetPlanSummarySuccessPresenter
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.plan_summary_service import PlanSummaryServiceImpl
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)
from arbeitszeit_web.presenters.show_my_accounts_presenter import (
    ShowMyAccountsPresenter,
)
from arbeitszeit_web.query_companies import QueryCompaniesPresenter
from arbeitszeit_web.query_plans import QueryPlansPresenter
from arbeitszeit_web.read_message import ReadMessageController, ReadMessagePresenter
from arbeitszeit_web.request_cooperation import RequestCooperationController
from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    ConfirmationUrlIndex,
    CoopSummaryUrlIndex,
    EndCoopUrlIndex,
    HidePlanUrlIndex,
    MessageUrlIndex,
    PlanSummaryUrlIndex,
    RenewPlanUrlIndex,
    TogglePlanAvailabilityUrlIndex,
)
from arbeitszeit_web.user_action_resolver import (
    UserActionResolver,
    UserActionResolverImpl,
)

from .translator import FlaskTranslator


class MemberModule(Module):
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
    def provide_message_url_index(
        self, member_index: MemberUrlIndex
    ) -> MessageUrlIndex:
        return member_index

    @provider
    def provide_end_coop_url_index(
        self, member_index: MemberUrlIndex
    ) -> EndCoopUrlIndex:
        return member_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return MemberTemplateIndex()


class CompanyModule(Module):
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
    def provide_message_url_index(
        self, company_index: CompanyUrlIndex
    ) -> MessageUrlIndex:
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
    def provide_end_coop_url_index(
        self, company_index: CompanyUrlIndex
    ) -> EndCoopUrlIndex:
        return company_index

    @provider
    def provide_template_index(self) -> TemplateIndex:
        return CompanyTemplateIndex()

    @provider
    def provide_end_cooperation_view(
        self,
        end_cooperation: EndCooperation,
        controller: EndCooperationController,
        presenter: EndCooperationPresenter,
        http_404_view: Http404View,
    ) -> EndCooperationView:
        return EndCooperationView(
            end_cooperation,
            controller,
            presenter,
            http_404_view,
        )

    @provider
    def provide_end_cooperation_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> EndCooperationController:
        return EndCooperationController(session, request)

    @provider
    def provide_end_cooperation_presenter(
        self,
        request: FlaskRequest,
        notifier: Notifier,
        plan_summary_index: PlanSummaryUrlIndex,
        coop_summary_index: CoopSummaryUrlIndex,
    ) -> EndCooperationPresenter:
        return EndCooperationPresenter(
            request, notifier, plan_summary_index, coop_summary_index
        )


class FlaskModule(Module):
    @provider
    def provide_email_configuration(self) -> EmailConfiguration:
        return FlaskEmailConfiguration()

    @provider
    def provide_send_confirmation_email_presenter(
        self, url_index: ConfirmationUrlIndex, email_configuration: EmailConfiguration
    ) -> SendConfirmationEmailPresenter:
        return SendConfirmationEmailPresenter(
            url_index=url_index, email_configuration=email_configuration
        )

    @provider
    def provide_token_deliverer(
        self, mail_service: MailService, presenter: SendConfirmationEmailPresenter
    ) -> TokenDeliverer:
        return FlaskTokenDeliverer(mail_service=mail_service, presenter=presenter)

    @provider
    def provide_read_message_view(
        self,
        read_message: ReadMessage,
        controller: ReadMessageController,
        presenter: ReadMessagePresenter,
        template_renderer: TemplateRenderer,
        template_index: TemplateIndex,
        http_404_view: Http404View,
    ) -> ReadMessageView:
        return ReadMessageView(
            read_message,
            controller,
            presenter,
            template_renderer,
            template_index,
            http_404_view,
        )

    @provider
    def provide_http_404_view(
        self, template_renderer: TemplateRenderer, template_index: TemplateIndex
    ) -> Http404View:
        return Http404View(
            template_index=template_index, template_renderer=template_renderer
        )

    @provider
    def provide_plan_summary_service(
        self, coop_url_index: CoopSummaryUrlIndex, trans: Translator
    ) -> PlanSummaryServiceImpl:
        return PlanSummaryServiceImpl(coop_url_index, trans)

    @provider
    def provide_query_companies_presenter(
        self, notifier: Notifier
    ) -> QueryCompaniesPresenter:
        return QueryCompaniesPresenter(user_notifier=notifier)

    @provider
    def provide_pay_means_of_production_presenter(
        self, notifier: Notifier
    ) -> PayMeansOfProductionPresenter:
        return PayMeansOfProductionPresenter(notifier)

    @provider
    def provide_list_all_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex
    ) -> ListAllCooperationsPresenter:
        return ListAllCooperationsPresenter(coop_index)

    @provider
    def provide_show_my_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex
    ) -> ShowMyCooperationsPresenter:
        return ShowMyCooperationsPresenter(coop_index)

    @provider
    def provide_show_my_plans_presenter(
        self,
        plan_index: PlanSummaryUrlIndex,
        coop_index: CoopSummaryUrlIndex,
        renew_plan_index: RenewPlanUrlIndex,
        hide_plan_index: HidePlanUrlIndex,
    ) -> ShowMyPlansPresenter:
        return ShowMyPlansPresenter(
            plan_index,
            coop_index,
            renew_plan_index,
            hide_plan_index,
        )

    @provider
    def provide_list_messages_presenter(
        self, message_index: MessageUrlIndex
    ) -> ListMessagesPresenter:
        return ListMessagesPresenter(message_index)

    @provider
    def provide_query_plans_presenter(
        self,
        plan_index: PlanSummaryUrlIndex,
        coop_index: CoopSummaryUrlIndex,
        notifier: Notifier,
    ) -> QueryPlansPresenter:
        return QueryPlansPresenter(plan_index, coop_index, user_notifier=notifier)

    @provider
    def provide_user_action_resolver(self) -> UserActionResolver:
        return UserActionResolverImpl()

    @provider
    def provide_get_plan_summary_success_presenter(
        self,
        trans: Translator,
        plan_summary_service: PlanSummaryServiceImpl,
    ) -> GetPlanSummarySuccessPresenter:
        return GetPlanSummarySuccessPresenter(trans, plan_summary_service)

    @provider
    def provide_get_plan_summary_company_success_presenter(
        self,
        toggle_availability_index: TogglePlanAvailabilityUrlIndex,
        end_coop_url_index: EndCoopUrlIndex,
        trans: Translator,
        plan_summary_service: PlanSummaryServiceImpl,
    ) -> GetPlanSummaryCompanySuccessPresenter:
        return GetPlanSummaryCompanySuccessPresenter(
            toggle_availability_index, end_coop_url_index, trans, plan_summary_service
        )

    @provider
    def provide_get_coop_summary_success_presenter(
        self, plan_index: PlanSummaryUrlIndex, end_coop_index: EndCoopUrlIndex
    ) -> GetCoopSummarySuccessPresenter:
        return GetCoopSummarySuccessPresenter(plan_index, end_coop_index)

    @provider
    def provide_transaction_repository(
        self, instance: TransactionRepository
    ) -> interfaces.TransactionRepository:
        return instance

    @provider
    def provide_template_renderer(self) -> TemplateRenderer:
        return FlaskTemplateRenderer()

    @provider
    def provide_user_template_renderer(
        self,
        flask_template_renderer: FlaskTemplateRenderer,
        session: FlaskSession,
        check_unread_messages_use_case: CheckForUnreadMessages,
        check_unread_messages_controller: CheckForUnreadMessagesController,
        check_unread_messages_presenter: CheckForUnreadMessagesPresenter,
    ) -> UserTemplateRenderer:
        return UserTemplateRenderer(
            flask_template_renderer,
            session,
            check_unread_messages_use_case,
            check_unread_messages_controller,
            check_unread_messages_presenter,
        )

    @provider
    def provide_list_messages_controller(
        self, session: FlaskSession
    ) -> ListMessagesController:
        return ListMessagesController(session)

    @provider
    def provide_request_cooperation_controller(
        self, session: FlaskSession
    ) -> RequestCooperationController:
        return RequestCooperationController(session)

    @provider
    def provide_read_message_controller(
        self, session: FlaskSession
    ) -> ReadMessageController:
        return ReadMessageController(session)

    @provider
    def provide_read_message_presenter(
        self, user_action_resolver: UserActionResolver
    ) -> ReadMessagePresenter:
        return ReadMessagePresenter(user_action_resolver)

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
    def provide_show_my_accounts_view(
        self,
        template_renderer: UserTemplateRenderer,
        controller: ShowMyAccountsController,
        use_case: ShowMyAccounts,
        presenter: ShowMyAccountsPresenter,
    ) -> ShowMyAccountsView:
        return ShowMyAccountsView(template_renderer, controller, use_case, presenter)

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
            interfaces.MessageRepository,  # type: ignore
            to=ClassProvider(MessageRepository),
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


class with_injection:
    def __init__(self, modules: Optional[List[Module]] = None) -> None:
        self._modules = modules if modules is not None else []

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self.get_injector().call_with_injection(
                inject(original_function), args=args, kwargs=kwargs
            )

        return wrapped_function

    def get_injector(self) -> Injector:
        all_modules: List[Module] = []
        all_modules.append(FlaskModule())
        all_modules += self._modules
        return Injector(all_modules)
