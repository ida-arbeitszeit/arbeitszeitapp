from injector import Module, provider

from arbeitszeit.use_cases import (
    AnswerCompanyWorkInvite,
    InviteWorkerToCompanyUseCase,
    ShowCompanyWorkInviteDetailsUseCase,
)
from arbeitszeit.use_cases.create_cooperation import CreateCooperation
from arbeitszeit.use_cases.end_cooperation import EndCooperation
from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit.use_cases.list_workers import ListWorkers
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase
from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorker,
)
from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
from arbeitszeit_flask.database.repositories import MemberRepository
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.template import (
    AnonymousUserTemplateRenderer,
    TemplateIndex,
    TemplateRenderer,
    UserTemplateRenderer,
)
from arbeitszeit_flask.views import (
    CompanyWorkInviteView,
    Http404View,
    InviteWorkerToCompanyView,
)
from arbeitszeit_flask.views.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from arbeitszeit_flask.views.company_dashboard_view import CompanyDashboardView
from arbeitszeit_flask.views.create_cooperation_view import CreateCooperationView
from arbeitszeit_flask.views.end_cooperation_view import EndCooperationView
from arbeitszeit_flask.views.invite_worker_to_company import (
    InviteWorkerGetRequestHandler,
    InviteWorkerPostRequestHandler,
)
from arbeitszeit_flask.views.pay_means_of_production import PayMeansOfProductionView
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_flask.views.signup_accountant_view import SignupAccountantView
from arbeitszeit_flask.views.signup_company_view import SignupCompanyView
from arbeitszeit_flask.views.signup_member_view import SignupMemberView
from arbeitszeit_flask.views.transfer_to_worker_view import TransferToWorkerView
from arbeitszeit_web.answer_company_work_invite import (
    AnswerCompanyWorkInviteController,
    AnswerCompanyWorkInvitePresenter,
)
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.controllers.list_workers_controller import ListWorkersController
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from arbeitszeit_web.controllers.register_accountant_controller import (
    RegisterAccountantController,
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
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.email import MailService
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
)
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)
from arbeitszeit_web.presenters.list_workers_presenter import ListWorkersPresenter
from arbeitszeit_web.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)
from arbeitszeit_web.presenters.show_company_work_invite_details_presenter import (
    ShowCompanyWorkInviteDetailsPresenter,
)
from arbeitszeit_web.presenters.show_my_accounts_presenter import (
    ShowMyAccountsPresenter,
)
from arbeitszeit_web.register_company import RegisterCompanyController
from arbeitszeit_web.register_member import RegisterMemberController


class ViewsModule(Module):
    @provider
    def provide_show_company_work_invite_details_view(
        self,
        details_use_case: ShowCompanyWorkInviteDetailsUseCase,
        details_presenter: ShowCompanyWorkInviteDetailsPresenter,
        details_controller: ShowCompanyWorkInviteDetailsController,
        answer_use_case: AnswerCompanyWorkInvite,
        answer_presenter: AnswerCompanyWorkInvitePresenter,
        answer_controller: AnswerCompanyWorkInviteController,
        http_404_view: Http404View,
        template_index: TemplateIndex,
        template_renderer: TemplateRenderer,
    ) -> CompanyWorkInviteView:
        return CompanyWorkInviteView(
            details_use_case=details_use_case,
            details_presenter=details_presenter,
            details_controller=details_controller,
            http_404_view=http_404_view,
            answer_use_case=answer_use_case,
            answer_presenter=answer_presenter,
            answer_controller=answer_controller,
            template_index=template_index,
            template_renderer=template_renderer,
        )

    @provider
    def provide_http_404_view(
        self, template_renderer: TemplateRenderer, template_index: TemplateIndex
    ) -> Http404View:
        return Http404View(
            template_index=template_index, template_renderer=template_renderer
        )

    @provider
    def provide_invite_worker_to_company_view(
        self,
        post_request_handler: InviteWorkerPostRequestHandler,
        get_request_handler: InviteWorkerGetRequestHandler,
    ) -> InviteWorkerToCompanyView:
        return InviteWorkerToCompanyView(
            post_request_handler=post_request_handler,
            get_request_handler=get_request_handler,
        )

    @provider
    def provide_invite_worker_post_request_handler(
        self,
        use_case: InviteWorkerToCompanyUseCase,
        presenter: InviteWorkerToCompanyPresenter,
        controller: InviteWorkerToCompanyController,
        template_renderer: TemplateRenderer,
        template_index: TemplateIndex,
    ) -> InviteWorkerPostRequestHandler:
        return InviteWorkerPostRequestHandler(
            use_case=use_case,
            presenter=presenter,
            controller=controller,
            template_renderer=template_renderer,
            template_index=template_index,
        )

    @provider
    def provide_invite_worker_get_request_handler(
        self,
        use_case: ListWorkers,
        presenter: ListWorkersPresenter,
        controller: ListWorkersController,
        template_index: TemplateIndex,
        template_renderer: TemplateRenderer,
    ) -> InviteWorkerGetRequestHandler:
        return InviteWorkerGetRequestHandler(
            template_index=template_index,
            template_renderer=template_renderer,
            controller=controller,
            use_case=use_case,
            presenter=presenter,
        )

    @provider
    def provide_show_my_accounts_view(
        self,
        template_renderer: TemplateRenderer,
        controller: ShowMyAccountsController,
        use_case: ShowMyAccounts,
        presenter: ShowMyAccountsPresenter,
    ) -> ShowMyAccountsView:
        return ShowMyAccountsView(template_renderer, controller, use_case, presenter)

    @provider
    def provide_signup_member_view(
        self,
        register_member: RegisterMemberUseCase,
        member_repository: MemberRepository,
        controller: RegisterMemberController,
        register_member_presenter: RegisterMemberPresenter,
        flask_session: FlaskSession,
    ) -> SignupMemberView:
        return SignupMemberView(
            register_member=register_member,
            member_repository=member_repository,
            controller=controller,
            register_member_presenter=register_member_presenter,
            flask_session=flask_session,
        )

    @provider
    def provide_signup_company_view(
        self,
        use_case: RegisterCompany,
        controller: RegisterCompanyController,
        presenter: RegisterCompanyPresenter,
        flask_session: FlaskSession,
    ) -> SignupCompanyView:
        return SignupCompanyView(
            register_company=use_case,
            controller=controller,
            flask_session=flask_session,
            presenter=presenter,
        )

    @provider
    def provide_accountant_invitation_email_view(
        self,
        mail_service: MailService,
        template_renderer: TemplateRenderer,
    ) -> AccountantInvitationEmailView:
        return AccountantInvitationEmailViewImpl(
            mail_service=mail_service,
            template_renderer=template_renderer,
        )

    @provider
    def provide_create_cooperation_view(
        self,
        create_cooperation: CreateCooperation,
        presenter: CreateCooperationPresenter,
        template_renderer: UserTemplateRenderer,
        session: FlaskSession,
    ) -> CreateCooperationView:
        return CreateCooperationView(
            create_cooperation, presenter, template_renderer, session
        )

    @provider
    def provide_company_dashboard_view(
        self,
        get_company_dashboard_use_case: GetCompanyDashboardUseCase,
        get_company_dashboard_presenter: GetCompanyDashboardPresenter,
        template_renderer: UserTemplateRenderer,
        flask_session: FlaskSession,
        http_404_view: Http404View,
    ) -> CompanyDashboardView:
        return CompanyDashboardView(
            get_company_dashboard_use_case,
            get_company_dashboard_presenter,
            template_renderer,
            flask_session,
            http_404_view,
        )

    @provider
    def provide_signup_accountant_view(
        self,
        template_renderer: AnonymousUserTemplateRenderer,
        controller: RegisterAccountantController,
        presenter: RegisterAccountantPresenter,
        use_case: RegisterAccountantUseCase,
    ) -> SignupAccountantView:
        return SignupAccountantView(
            template_renderer=template_renderer,
            controller=controller,
            presenter=presenter,
            use_case=use_case,
        )

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
