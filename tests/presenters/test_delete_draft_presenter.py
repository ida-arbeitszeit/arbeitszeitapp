from unittest import TestCase

from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit_web.presenters.delete_draft_presenter import DeleteDraftPresenter
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(DeleteDraftPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.session = self.injector.get(FakeSession)

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
    ) -> DeleteDraftUseCase.Response:
        return DeleteDraftUseCase.Response(product_name=product_name)
