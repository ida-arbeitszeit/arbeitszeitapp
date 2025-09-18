from arbeitszeit.interactors.delete_draft import DeleteDraftInteractor
from arbeitszeit_web.www.presenters.delete_draft_presenter import DeleteDraftPresenter
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(DeleteDraftPresenter)

    def test_that_user_gets_redirected_to_my_plans(self) -> None:
        response = self.get_response()
        view_model = self.presenter.present_draft_deletion(response)
        self.assertEqual(view_model.redirect_target, self.url_index.get_my_plans_url())

    def test_that_user_gets_redirected_to_next_url_from_session_if_set(self) -> None:
        expected_url = "/a/b/c"
        self.session.set_next_url(expected_url)
        response = self.get_response()
        view_model = self.presenter.present_draft_deletion(response)
        self.assertEqual(view_model.redirect_target, expected_url)

    def test_that_user_gets_message_confirming_successful_deletion(self) -> None:
        response = self.get_response()
        self.presenter.present_draft_deletion(response)
        self.assertTrue(self.notifier.infos)

    def test_for_correct_user_message(self) -> None:
        expected_draft_name = "test plan draft"
        response = self.get_response(product_name=expected_draft_name)
        self.presenter.present_draft_deletion(response)
        self.assertIn(
            self.translator.gettext("Plan draft %(product_name)s was deleted")
            % dict(product_name=expected_draft_name),
            self.notifier.infos,
        )

    def get_response(
        self, product_name: str = "test draft name"
    ) -> DeleteDraftInteractor.Response:
        return DeleteDraftInteractor.Response(product_name=product_name)
