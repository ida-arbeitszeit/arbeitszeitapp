from uuid import uuid4

from arbeitszeit.use_cases.get_accountant_dashboard import GetAccountantDashboardUseCase
from arbeitszeit_web.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)

from .base_test_case import BaseTestCase
from .url_index import UrlIndexTestImpl


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetAccountantDashboardPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_that_view_model_contains_url_to_unreviewed_plans_list_view(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        self.assertEqual(
            view_model.unreviewed_plans_view_url,
            self.url_index.get_unreviewed_plans_list_view_url(),
        )

    def test_that_view_model_contains_accountant_id(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.accountant_id, str)

    def test_that_view_model_contains_accountant_name(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.name, str)

    def test_that_view_model_contains_accountant_email(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.create_dashboard_view_model(response)
        assert isinstance(view_model.email, str)

    def get_use_case_response(self) -> GetAccountantDashboardUseCase.Response:
        return GetAccountantDashboardUseCase.Response(
            accountant_id=uuid4(), name="test name", email="test@mail.com"
        )
