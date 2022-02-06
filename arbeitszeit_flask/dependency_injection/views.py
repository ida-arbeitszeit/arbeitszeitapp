from injector import Module, provider

from arbeitszeit.use_cases import (
    AnswerCompanyWorkInvite,
    InviteWorkerToCompany,
    ReadMessage,
    ShowCompanyWorkInviteDetailsUseCase,
)
from arbeitszeit_flask.template import TemplateIndex, TemplateRenderer
from arbeitszeit_flask.views import (
    CompanyWorkInviteView,
    Http404View,
    InviteWorkerToCompanyView,
    ReadMessageView,
)
from arbeitszeit_flask.views.invite_worker_to_company import (
    InviteWorkerPostRequestHandler,
)
from arbeitszeit_web.answer_company_work_invite import (
    AnswerCompanyWorkInviteController,
    AnswerCompanyWorkInvitePresenter,
)
from arbeitszeit_web.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
)
from arbeitszeit_web.presenters.show_company_work_invite_details_presenter import (
    ShowCompanyWorkInviteDetailsPresenter,
)
from arbeitszeit_web.read_message import ReadMessageController, ReadMessagePresenter


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
    def provide_invite_worker_to_company_view(
        self,
        template_index: TemplateIndex,
        template_renderer: TemplateRenderer,
        post_request_handler: InviteWorkerPostRequestHandler,
    ) -> InviteWorkerToCompanyView:
        return InviteWorkerToCompanyView(
            template_index=template_index,
            template_renderer=template_renderer,
            post_request_handler=post_request_handler,
        )

    @provider
    def provide_invite_worker_post_request_handler(
        self,
        use_case: InviteWorkerToCompany,
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
