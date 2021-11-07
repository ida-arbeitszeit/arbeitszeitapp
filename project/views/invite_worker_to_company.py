from dataclasses import dataclass
from uuid import UUID

from flask import Response, flash, render_template

from arbeitszeit.use_cases import InviteWorkerToCompany
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
    ViewModel,
)
from project.forms import InviteWorkerToCompanyForm


@dataclass
class InviteWorkerToCompanyView:
    invite_worker: InviteWorkerToCompany
    presenter: InviteWorkerToCompanyPresenter
    controller: InviteWorkerToCompanyController
    template_name: str

    def respond_to_get(self, form: InviteWorkerToCompanyForm) -> Response:
        view_model = ViewModel(notifications=[])
        return Response(
            render_template(self.template_name, form=form, view_model=view_model)
        )

    def respond_to_post(
        self, current_user_id: UUID, form: InviteWorkerToCompanyForm
    ) -> Response:
        if not form.validate():
            return self._display_form_errors(form)
        try:
            use_case_request = self.controller.import_request_data(
                current_user_id, form
            )
        except ValueError:
            return self._display_form_errors(form)
        use_case_response = self.invite_worker(use_case_request)
        view_model = self.presenter.present(use_case_response)
        for notification in view_model.notifications:
            flash(notification)
        return Response(
            render_template(self.template_name, form=form, view_model=view_model),
            status=200,
        )

    def _display_form_errors(self, form: InviteWorkerToCompanyForm) -> Response:
        view_model = ViewModel(notifications=["Ungültiges Formular"])
        return Response(
            render_template(self.template_name, form=form, view_model=view_model),
            status=400,
        )
