from arbeitszeit.use_cases.edit_draft import Response
from arbeitszeit_web.www.presenters.edit_draft_presenter import EditDraftPresenter
from tests.www.base_test_case import BaseTestCase


class EditDraftPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EditDraftPresenter)

    def test_unsuccessful_response_leads_to_redirect_url_being_none(self) -> None:
        view_model = self.presenter.render_response(response=Response(is_success=False))
        assert view_model.redirect_url is None

    def test_that_successful_response_leads_to_redirect_url_pointing_to_my_plans_view(
        self,
    ) -> None:
        view_model = self.presenter.render_response(response=Response(is_success=True))
        assert view_model.redirect_url == self.url_index.get_my_plans_url()
