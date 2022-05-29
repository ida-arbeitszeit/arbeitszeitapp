from unittest import TestCase

from arbeitszeit.use_cases import CheckForUnreadMessages
from arbeitszeit_web.check_for_unread_message import CheckForUnreadMessagesPresenter

from .dependency_injection import get_dependency_injector


class CheckForUnreadMessagesPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(CheckForUnreadMessagesPresenter)

    def test_when_response_has_unread_messages_then_show_indicator(self) -> None:
        response = CheckForUnreadMessages.Response(has_unread_messages=True)
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.show_unread_messages_indicator)

    def test_when_response_doesnt_have_unread_messages_then_dont_show_indicator(
        self,
    ) -> None:
        response = CheckForUnreadMessages.Response(has_unread_messages=False)
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_unread_messages_indicator)

    def test_anonymous_view_model_does_not_indicate_unread_messages(self) -> None:
        view_model = self.presenter.anonymous_view_model()
        self.assertFalse(view_model.show_unread_messages_indicator)
