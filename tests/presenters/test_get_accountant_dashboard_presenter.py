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
        view_model = self.presenter.create_dashboard_view_model()
        self.assertEqual(
            view_model.unreviewed_plans_view_url,
            self.url_index.get_unreviewed_plans_list_view_url(),
        )
