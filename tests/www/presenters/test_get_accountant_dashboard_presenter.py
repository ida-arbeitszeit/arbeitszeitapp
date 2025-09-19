from uuid import uuid4

from arbeitszeit.interactors.get_accountant_dashboard import (
    GetAccountantDashboardInteractor,
)
from arbeitszeit_web.www.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetAccountantDashboardPresenter)

    def test_that_view_model_contains_url_to_unreviewed_plans_list_view(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        self.assertEqual(
            view_model.unreviewed_plans_view_url,
            self.url_index.get_unreviewed_plans_list_view_url(),
        )

    def test_that_view_model_contains_accountant_id(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.accountant_id, str)

    def test_that_view_model_contains_accountant_name(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.name, str)

    def test_that_view_model_contains_accountant_email(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.email, str)

    def get_interactor_response(self) -> GetAccountantDashboardInteractor.Response:
        return GetAccountantDashboardInteractor.Response(
            accountant_id=uuid4(), name="test name", email="test@mail.com"
        )
