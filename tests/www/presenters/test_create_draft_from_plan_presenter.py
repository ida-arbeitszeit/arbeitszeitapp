from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors import create_draft_from_plan as interactor
from arbeitszeit_web.www.presenters.create_draft_from_plan_presenter import (
    CreateDraftFromPlanPresenter,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class CreateDraftFromPlanPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateDraftFromPlanPresenter)

    def test_that_user_is_redirected_to_plan_details_view_on_success(self) -> None:
        request = FakeRequest()
        expected_draft_id = uuid4()
        response = interactor.Response(draft=expected_draft_id)
        view_model = self.presenter.render_response(response, request)
        assert view_model.redirect_url == self.url_index.get_draft_details_url(
            expected_draft_id
        )

    @parameterized.expand(
        [
            ("test",),
            ("other/test"),
        ]
    )
    def test_that_user_is_redirected_to_last_visited_page_on_failure(
        self, expected_url: str
    ) -> None:
        request = FakeRequest()
        response = interactor.Response(draft=None)
        request.set_header("Referer", expected_url)
        view_model = self.presenter.render_response(response, request)
        assert view_model.redirect_url == expected_url

    def test_that_user_is_redirected_to_company_plans_list_if_referer_is_not_set(
        self,
    ) -> None:
        request = FakeRequest()
        response = interactor.Response(draft=None)
        request.set_header("Referer", None)
        view_model = self.presenter.render_response(response, request)
        assert view_model.redirect_url == self.url_index.get_my_plans_url()

    def test_that_user_is_notified_about_successful_draft_creation_on_success(
        self,
    ) -> None:
        request = FakeRequest()
        expected_draft_id = uuid4()
        response = interactor.Response(draft=expected_draft_id)
        self.presenter.render_response(response, request)
        assert (
            self.translator.gettext("A new draft was created from an expired plan.")
            in self.notifier.infos
        )
