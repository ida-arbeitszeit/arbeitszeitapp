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
from arbeitszeit.token import InvitationTokenValidator, TokenDeliverer, TokenService
from arbeitszeit.use_cases import (
    CheckForUnreadMessages,
    EndCooperation,
    GetCompanySummary,
    ReadWorkerInviteMessage,
)
from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit.use_cases.get_draft_summary import GetDraftSummary
from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit.use_cases.list_workers import ListWorkers
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit.use_cases.register_company.company_registration_message_presenter import (
    CompanyRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.register_member.member_registration_message_presenter import (
    MemberRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorker,
)
from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
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
    WorkerInviteMessageRepository,
    WorkerInviteRepository,
)
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import db
from arbeitszeit_flask.flask_colors import FlaskColors
from arbeitszeit_flask.flask_plotter import FlaskPlotter
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
    GeneralUrlIndex,
    MemberUrlIndex,
)
from arbeitszeit_flask.views import (
    EndCooperationView,
    Http404View,
    ReadWorkerInviteMessageView,
)
from arbeitszeit_flask.views.create_draft_view import CreateDraftView
from arbeitszeit_flask.views.pay_means_of_production import PayMeansOfProductionView
from arbeitszeit_flask.views.transfer_to_worker_view import TransferToWorkerView
from arbeitszeit_web.answer_company_work_invite import (
    AnswerCompanyWorkInviteController,
    AnswerCompanyWorkInvitePresenter,
)
from arbeitszeit_web.check_for_unread_message import (
    CheckForUnreadMessagesController,
    CheckForUnreadMessagesPresenter,
)
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
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_member_profile_info import GetMemberProfileInfoPresenter
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from arbeitszeit_web.get_plan_summary_member import GetPlanSummarySuccessPresenter
from arbeitszeit_web.get_prefilled_draft_data import (
    GetPrefilledDraftDataPresenter,
    PrefilledDraftDataController,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
)
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.plan_summary_service import PlanSummaryServiceImpl
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailPresenter,
    AccountantInvitationEmailView,
)
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.presenters.get_latest_activated_plans_presenter import (
    GetLatestActivatedPlansPresenter,
)
from arbeitszeit_web.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailPresenter,
    RegistrationEmailTemplate,
)
from arbeitszeit_web.presenters.seek_plan_approval import SeekPlanApprovalPresenter
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)
from arbeitszeit_web.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_company_work_invite_details_presenter import (
    ShowCompanyWorkInviteDetailsPresenter,
)
from arbeitszeit_web.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)
from arbeitszeit_web.query_companies import QueryCompaniesPresenter
from arbeitszeit_web.query_plans import QueryPlansPresenter
from arbeitszeit_web.read_worker_invite_message import (
    ReadWorkerInviteMessageController,
    ReadWorkerInviteMessagePresenter,
)
from arbeitszeit_web.request_cooperation import (
    RequestCooperationController,
    RequestCooperationPresenter,
)
from arbeitszeit_web.session import Session
from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    AnswerCompanyWorkInviteUrlIndex,
    CompanySummaryUrlIndex,
    ConfirmationUrlIndex,
    CoopSummaryUrlIndex,
    EndCoopUrlIndex,
    HidePlanUrlIndex,
    ListMessagesUrlIndex,
    PlanSummaryUrlIndex,
    PlotsUrlIndex,
    RenewPlanUrlIndex,
    RequestCoopUrlIndex,
    TogglePlanAvailabilityUrlIndex,
    WorkInviteMessageUrlIndex,
)

from .views import ViewsModule

__all__ = [
    "ViewsModule",
]


class MemberModule(Module):
    @provider
    def provide_get_member_profile_info_presenter(
        self, translator: Translator
    ) -> GetMemberProfileInfoPresenter:
        return GetMemberProfileInfoPresenter(translator=translator)

    @provider
    def provide_list_messages_url_index(
        self, member_index: MemberUrlIndex
    ) -> ListMessagesUrlIndex:
        return member_index

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
    def provide_answer_company_work_invite_url_index(
        self, url_index: MemberUrlIndex
    ) -> AnswerCompanyWorkInviteUrlIndex:
        return url_index

    @provider
    def provide_work_invite_message_url_index(
        self, url_index: MemberUrlIndex
    ) -> WorkInviteMessageUrlIndex:
        return url_index


class CompanyModule(Module):
    @provider
    def provide_list_messages_url_index(
        self, company_index: CompanyUrlIndex
    ) -> ListMessagesUrlIndex:
        return company_index

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
    def provide_request_cooperation_presenter(
        self, translator: Translator
    ) -> RequestCooperationPresenter:
        return RequestCooperationPresenter(translator)

    @provider
    def provide_send_work_certificates_to_worker_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> SendWorkCertificatesToWorkerController:
        return SendWorkCertificatesToWorkerController(session, request)

    @provider
    def provide_send_work_certificates_to_worker_presenter(
        self, notifier: Notifier, translator: Translator
    ) -> SendWorkCertificatesToWorkerPresenter:
        return SendWorkCertificatesToWorkerPresenter(notifier, translator)

    @provider
    def provide_transfer_to_worker_view(
        self,
        template_renderer: UserTemplateRenderer,
        send_work_certificates_to_worker: SendWorkCertificatesToWorker,
        controller: SendWorkCertificatesToWorkerController,
        presenter: SendWorkCertificatesToWorkerPresenter,
        list_workers: ListWorkers,
    ) -> TransferToWorkerView:
        return TransferToWorkerView(
            template_renderer,
            send_work_certificates_to_worker,
            controller,
            presenter,
            list_workers,
        )

    @provider
    def provide_end_cooperation_presenter(
        self,
        request: FlaskRequest,
        notifier: Notifier,
        plan_summary_index: PlanSummaryUrlIndex,
        coop_summary_index: CoopSummaryUrlIndex,
        translator: Translator,
    ) -> EndCooperationPresenter:
        return EndCooperationPresenter(
            request, notifier, plan_summary_index, coop_summary_index, translator
        )

    @provider
    def provide_pay_means_of_production_controller(
        self, session: FlaskSession, request: FlaskRequest
    ) -> PayMeansOfProductionController:
        return PayMeansOfProductionController(session, request)

    @provider
    def provide_pay_means_of_production_view(
        self,
        controller: PayMeansOfProductionController,
        pay_means_of_production: PayMeansOfProduction,
        presenter: PayMeansOfProductionPresenter,
        template_renderer: UserTemplateRenderer,
    ) -> PayMeansOfProductionView:
        return PayMeansOfProductionView(
            controller, pay_means_of_production, presenter, template_renderer
        )

    @provider
    def provide_answer_company_work_invite_url_index(
        self, url_index: CompanyUrlIndex
    ) -> AnswerCompanyWorkInviteUrlIndex:
        return url_index

    @provider
    def provide_show_prd_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowPRDAccountDetailsPresenter:
        return ShowPRDAccountDetailsPresenter(
            translator=translator,
            url_index=url_index,
            datetime_service=datetime_service,
        )

    @provider
    def provide_show_r_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowRAccountDetailsPresenter:
        return ShowRAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_show_a_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowAAccountDetailsPresenter:
        return ShowAAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_show_p_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowPAccountDetailsPresenter:
        return ShowPAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_prefilled_draft_data_controller(
        self, session: Session
    ) -> PrefilledDraftDataController:
        return PrefilledDraftDataController(session=session)

    @provider
    def provide_create_draft_view(
        self,
        request: FlaskRequest,
        session: Session,
        notifier: Notifier,
        translator: Translator,
        prefilled_data_controller: PrefilledDraftDataController,
        get_plan_summary_company: GetPlanSummaryCompany,
        create_draft: CreatePlanDraft,
        get_draft_summary: GetDraftSummary,
        get_prefilled_draft_data_presenter: GetPrefilledDraftDataPresenter,
        template_renderer: UserTemplateRenderer,
        http_404_view: Http404View,
    ) -> CreateDraftView:
        return CreateDraftView(
            request,
            session,
            notifier,
            translator,
            prefilled_data_controller,
            get_plan_summary_company,
            create_draft,
            get_draft_summary,
            get_prefilled_draft_data_presenter,
            template_renderer,
            http_404_view,
        )

    @provider
    def provide_get_company_transactions_presenter(
        self, translator: Translator
    ) -> GetCompanyTransactionsPresenter:
        return GetCompanyTransactionsPresenter(translator=translator)

    @provider
    def provide_work_invite_message_url_index(
        self, url_index: CompanyUrlIndex
    ) -> WorkInviteMessageUrlIndex:
        return url_index


class FlaskModule(Module):
    @provider
    def provide_invitation_token_validator(
        self, validator: FlaskTokenService
    ) -> InvitationTokenValidator:
        return validator

    @provider
    def provide_register_accountant_presenter(
        self,
        notifier: FlaskFlashNotifier,
        session: FlaskSession,
        translator: FlaskTranslator,
        dashboard_url_index: GeneralUrlIndex,
    ) -> RegisterAccountantPresenter:
        return RegisterAccountantPresenter(
            notifier=notifier,
            session=session,
            translator=translator,
            dashboard_url_index=dashboard_url_index,
        )

    @provider
    def provide_accountant_invitation_presenter(
        self,
        view: AccountantInvitationEmailView,
        email_configuration: EmailConfiguration,
        translator: Translator,
        invitation_url_index: GeneralUrlIndex,
    ) -> AccountantInvitationPresenter:
        return AccountantInvitationEmailPresenter(
            invitation_view=view,
            email_configuration=email_configuration,
            translator=translator,
            invitation_url_index=invitation_url_index,
        )

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
    def provide_register_member_presenter(
        self, session: Session, translator: Translator
    ) -> RegisterMemberPresenter:
        return RegisterMemberPresenter(session=session, translator=translator)

    @provider
    def provide_register_company_presenter(
        self, session: Session, translator: Translator
    ) -> RegisterCompanyPresenter:
        return RegisterCompanyPresenter(session=session, translator=translator)

    @provider
    def provide_registration_email_presenter(
        self,
        email_sender: MailService,
        address_book: UserAddressBook,
        email_template: RegistrationEmailTemplate,
        url_index: ConfirmationUrlIndex,
        email_configuration: EmailConfiguration,
        translator: Translator,
    ) -> RegistrationEmailPresenter:
        return RegistrationEmailPresenter(
            email_sender=email_sender,
            address_book=address_book,
            member_email_template=email_template,
            company_email_template=email_template,
            url_index=url_index,
            email_configuration=email_configuration,
            translator=translator,
        )

    @provider
    def provide_member_registration_message_presenter(
        self, presenter: RegistrationEmailPresenter
    ) -> MemberRegistrationMessagePresenter:
        return presenter

    @provider
    def provide_company_registration_message_presenter(
        self, presenter: RegistrationEmailPresenter
    ) -> CompanyRegistrationMessagePresenter:
        return presenter

    @provider
    def provide_member_registration_email_template(
        self,
    ) -> RegistrationEmailTemplate:
        return MemberRegistrationEmailTemplateImpl()

    @provider
    def provide_get_statistics_presenter(
        self,
        translator: Translator,
        plotter: Plotter,
        colors: Colors,
        url_index: PlotsUrlIndex,
    ) -> GetStatisticsPresenter:
        return GetStatisticsPresenter(
            translator=translator, plotter=plotter, colors=colors, url_index=url_index
        )

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
    def provide_list_workers_controller(
        self, session: Session
    ) -> ListWorkersController:
        return ListWorkersController(session=session)

    @provider
    def provide_show_company_work_invite_details_presenter(
        self, url_index: AnswerCompanyWorkInviteUrlIndex, translator: Translator
    ) -> ShowCompanyWorkInviteDetailsPresenter:
        return ShowCompanyWorkInviteDetailsPresenter(url_index, translator)

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
    def provide_answer_company_work_invite_presenter(
        self,
        notifier: Notifier,
        url_index: ListMessagesUrlIndex,
        translator: Translator,
    ) -> AnswerCompanyWorkInvitePresenter:
        return AnswerCompanyWorkInvitePresenter(
            notifier, url_index=url_index, translator=translator
        )

    @provider
    def provide_email_configuration(self) -> EmailConfiguration:
        return FlaskEmailConfiguration()

    @provider
    def provide_send_confirmation_email_presenter(
        self,
        url_index: ConfirmationUrlIndex,
        email_configuration: EmailConfiguration,
        translator: Translator,
    ) -> SendConfirmationEmailPresenter:
        return SendConfirmationEmailPresenter(
            url_index=url_index,
            email_configuration=email_configuration,
            translator=translator,
        )

    @provider
    def provide_token_deliverer(
        self, mail_service: MailService, presenter: SendConfirmationEmailPresenter
    ) -> TokenDeliverer:
        return FlaskTokenDeliverer(mail_service=mail_service, presenter=presenter)

    @provider
    def provide_read_worker_invite_message_view(
        self,
        read_message: ReadWorkerInviteMessage,
        controller: ReadWorkerInviteMessageController,
        presenter: ReadWorkerInviteMessagePresenter,
        template_renderer: TemplateRenderer,
        http_404_view: Http404View,
    ) -> ReadWorkerInviteMessageView:
        return ReadWorkerInviteMessageView(
            read_message,
            controller,
            presenter,
            template_renderer,
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
        self,
        coop_url_index: CoopSummaryUrlIndex,
        company_url_index: CompanySummaryUrlIndex,
        translator: Translator,
    ) -> PlanSummaryServiceImpl:
        return PlanSummaryServiceImpl(coop_url_index, company_url_index, translator)

    @provider
    def provide_query_companies_presenter(
        self,
        notifier: Notifier,
        company_url_index: CompanySummaryUrlIndex,
        translator: Translator,
    ) -> QueryCompaniesPresenter:
        return QueryCompaniesPresenter(
            user_notifier=notifier,
            company_url_index=company_url_index,
            translator=translator,
        )

    @provider
    def provide_pay_means_of_production_presenter(
        self, notifier: Notifier, trans: Translator
    ) -> PayMeansOfProductionPresenter:
        return PayMeansOfProductionPresenter(notifier, trans)

    @provider
    def provide_list_all_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex
    ) -> ListAllCooperationsPresenter:
        return ListAllCooperationsPresenter(coop_index)

    @provider
    def provide_show_my_cooperations_presenter(
        self, coop_index: CoopSummaryUrlIndex, translator: Translator
    ) -> ShowMyCooperationsPresenter:
        return ShowMyCooperationsPresenter(coop_index, translator=translator)

    @provider
    def provide_show_my_plans_presenter(
        self,
        plan_index: PlanSummaryUrlIndex,
        coop_index: CoopSummaryUrlIndex,
        renew_plan_index: RenewPlanUrlIndex,
        hide_plan_index: HidePlanUrlIndex,
        translator: Translator,
    ) -> ShowMyPlansPresenter:
        return ShowMyPlansPresenter(
            plan_index, coop_index, renew_plan_index, hide_plan_index, translator
        )

    @provider
    def provide_list_messages_presenter(
        self,
        message_index: WorkInviteMessageUrlIndex,
        datetime_service: DatetimeService,
        translator: Translator,
    ) -> ListMessagesPresenter:
        return ListMessagesPresenter(message_index, datetime_service, translator)

    @provider
    def provide_query_plans_presenter(
        self,
        plan_index: PlanSummaryUrlIndex,
        company_index: CompanySummaryUrlIndex,
        coop_index: CoopSummaryUrlIndex,
        notifier: Notifier,
        trans: Translator,
    ) -> QueryPlansPresenter:
        return QueryPlansPresenter(
            plan_index, company_index, coop_index, notifier, trans
        )

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
        request_coop_url_index: RequestCoopUrlIndex,
        trans: Translator,
        plan_summary_service: PlanSummaryServiceImpl,
    ) -> GetPlanSummaryCompanySuccessPresenter:
        return GetPlanSummaryCompanySuccessPresenter(
            toggle_availability_index,
            end_coop_url_index,
            request_coop_url_index,
            trans,
            plan_summary_service,
        )

    @provider
    def provide_get_coop_summary_success_presenter(
        self, plan_index: PlanSummaryUrlIndex, end_coop_index: EndCoopUrlIndex
    ) -> GetCoopSummarySuccessPresenter:
        return GetCoopSummarySuccessPresenter(plan_index, end_coop_index)

    @provider
    def provide_get_company_summary_success_presenter(
        self, plan_index: PlanSummaryUrlIndex, translator: Translator
    ) -> GetCompanySummarySuccessPresenter:
        return GetCompanySummarySuccessPresenter(plan_index, translator)

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
    def provide_check_for_unread_messages_controller(
        self, session: Session
    ) -> CheckForUnreadMessagesController:
        return CheckForUnreadMessagesController(session)

    @provider
    def provide_invite_worker_to_company_controller(
        self, session: Session
    ) -> InviteWorkerToCompanyController:
        return InviteWorkerToCompanyController(session)

    @provider
    def provide_invite_worker_to_company_presenter(
        self, translator: Translator
    ) -> InviteWorkerToCompanyPresenter:
        return InviteWorkerToCompanyPresenter(translator)

    @provider
    def provide_user_template_renderer(
        self,
        flask_template_renderer: FlaskTemplateRenderer,
        session: Session,
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
        self, session: Session
    ) -> ListMessagesController:
        return ListMessagesController(session)

    @provider
    def provide_request_cooperation_controller(
        self, session: Session, translator: Translator
    ) -> RequestCooperationController:
        return RequestCooperationController(session, translator)

    @provider
    def provide_read_message_controller(
        self, session: Session
    ) -> ReadWorkerInviteMessageController:
        return ReadWorkerInviteMessageController(session)

    @provider
    def provide_session(self, flask_session: FlaskSession) -> Session:
        return flask_session

    @provider
    def provide_read_worker_invite_message_presenter(
        self,
    ) -> ReadWorkerInviteMessagePresenter:
        return ReadWorkerInviteMessagePresenter()

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
    def provide_get_latest_activated_plans_presenter(
        self, url_index: PlanSummaryUrlIndex, datetime_service: DatetimeService
    ) -> GetLatestActivatedPlansPresenter:
        return GetLatestActivatedPlansPresenter(
            url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_seek_plan_approval_presenter(
        self, notifier: Notifier, translator: Translator
    ) -> SeekPlanApprovalPresenter:
        return SeekPlanApprovalPresenter(
            notifier=notifier,
            translator=translator,
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
        binder.bind(
            interfaces.WorkerInviteMessageRepository,  # type: ignore
            to=ClassProvider(WorkerInviteMessageRepository),
        )
        binder.bind(TokenService, to=ClassProvider(FlaskTokenService))  # type: ignore
        binder.bind(UserAddressBook, to=ClassProvider(inject(UserAddressBookImpl)))  # type: ignore


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
        all_modules.append(ViewsModule())
        all_modules += self._modules
        return Injector(all_modules)
