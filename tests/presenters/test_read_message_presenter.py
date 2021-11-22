from unittest import TestCase

from arbeitszeit.use_cases import ReadMessageSuccess
from arbeitszeit_web.read_message import ReadMessagePresenter


class ReadMessagePresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = ReadMessagePresenter()
        self.use_case_response = ReadMessageSuccess(
            message_title="test title",
            message_content="message content",
            sender_remarks=None,
            user_action=None,
        )

    def test_correct_message_title_from_use_case_is_propagated_to_view_model(
        self,
    ) -> None:
        self.use_case_response.message_title = "test title"
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.title, "test title")

    def test_correct_message_content_is_shown_in_view_model(self) -> None:
        self.use_case_response.message_content = "test content"
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.content, "test content")
