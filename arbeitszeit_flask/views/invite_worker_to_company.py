from __future__ import annotations

from dataclasses import dataclass

from flask import Response, flash

from arbeitszeit.use_cases import InviteWorkerToCompany
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import InviteWorkerToCompanyForm
from arbeitszeit_flask.template import TemplateIndex, TemplateRenderer
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
    ViewModel,
)


@dataclass
class InviteWorkerToCompanyView:
    template_index: TemplateIndex
    template_renderer: TemplateRenderer
    post_request_handler: InviteWorkerPostRequestHandler

    def respond_to_get(self, form: InviteWorkerToCompanyForm) -> Response:
        template_name = self.template_index.get_template_by_name(
            "invite_worker_to_company"
        )
        view_model = ViewModel(notifications=[])
        return Response(
            self.template_renderer.render_template(
                template_name, context=dict(form=form, view_model=view_model)
            )
        )

    def respond_to_post(self, form: InviteWorkerToCompanyForm) -> Response:
        return self.post_request_handler.respond_to_post(form)


@dataclass
class InviteWorkerPostRequestHandler:
    use_case: InviteWorkerToCompany
    presenter: InviteWorkerToCompanyPresenter
    controller: InviteWorkerToCompanyController
    template_renderer: TemplateRenderer
    template_index: TemplateIndex

    @commit_changes
    def respond_to_post(self, form: InviteWorkerToCompanyForm) -> Response:
        template_name = self.template_index.get_template_by_name(
            "invite_worker_to_company"
        )
        if not form.validate():
            return self._display_form_errors(form, template_name)
        try:
            use_case_request = self.controller.import_request_data(form)
        except ValueError:
            return self._display_form_errors(form, template_name)
        use_case_response = self.use_case(use_case_request)
        view_model = self.presenter.present(use_case_response)
        for notification in view_model.notifications:
            flash(notification)
        return Response(
            self.template_renderer.render_template(
                template_name, context=dict(form=form, view_model=view_model)
            ),
            status=200,
        )

    def _display_form_errors(
        self, form: InviteWorkerToCompanyForm, template_name: str
    ) -> Response:
        view_model = ViewModel(notifications=["Ungültiges Formular"])
        return Response(
            self.template_renderer.render_template(
                template_name, context=dict(form=form, view_model=view_model)
            ),
            status=400,
        )
