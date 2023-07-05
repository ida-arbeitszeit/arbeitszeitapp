from dataclasses import dataclass

from flask import Response

from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_web.www.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from arbeitszeit_web.www.presenters.show_my_accounts_presenter import (
    ShowMyAccountsPresenter,
)


@dataclass
class ShowMyAccountsView:
    template_renderer: TemplateRenderer
    controller: ShowMyAccountsController
    use_case: ShowMyAccounts
    presenter: ShowMyAccountsPresenter

    def respond_to_get(self) -> Response:
        use_case_request = self.controller.create_request()
        response = self.use_case(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            self.template_renderer.render_template(
                "company/my_accounts.html",
                context=dict(
                    view_model=view_model,
                ),
            )
        )
