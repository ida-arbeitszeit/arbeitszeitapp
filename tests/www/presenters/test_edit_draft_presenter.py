from parameterized import parameterized

from arbeitszeit.interactors.edit_draft import Response
from arbeitszeit_web.www.presenters.edit_draft_presenter import EditDraftPresenter
from tests.www.base_test_case import BaseTestCase


class EditDraftPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EditDraftPresenter)

    @parameterized.expand(
        [
            (Response.RejectionReason.NOT_FOUND,),
            (Response.RejectionReason.UNAUTHORIZED,),
        ]
    )
    def test_unsuccessful_response_leads_to_redirect_url_being_none(
        self,
        rejection_reason: Response.RejectionReason,
    ) -> None:
        view_model = self.presenter.render_response(
            response=Response(rejection_reason=rejection_reason)
        )
        assert view_model.redirect_url is None

    def test_that_successful_response_leads_to_redirect_url_pointing_to_my_plans_view(
        self,
    ) -> None:
        view_model = self.presenter.render_response(
            response=Response(rejection_reason=None)
        )
        assert view_model.redirect_url == self.url_index.get_my_plans_url()
