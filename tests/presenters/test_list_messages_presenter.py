from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from hypothesis import given, strategies

from arbeitszeit.use_cases import ListedMessage, ListMessagesResponse
from arbeitszeit_web.list_messages import ListMessagesPresenter


class ListMessagesPresenterTests(TestCase):
    def setUp(self) -> None:
        self.url_index = FakeUrlIndex()
        self.presenter = ListMessagesPresenter(self.url_index)

    def test_view_model_contains_no_messages_when_non_were_provided(self) -> None:
        response = ListMessagesResponse(messages=[])
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.messages)

    def test_view_model_contains_messages_when_one_was_provided(self) -> None:
        response = self._create_response_with_one_message()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.messages)

    @given(title=strategies.text())
    def test_title_is_propagated_to_view_model(self, title: str) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(title=title)
        )
        self.assertEqual(view_model.messages[0].title, title)

    @given(sender_name=strategies.text())
    def test_sender_name_is_propagated_to_view_model(self, sender_name: str) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(sender_name=sender_name)
        )
        self.assertEqual(view_model.messages[0].sender_name, sender_name)

    def test_dont_show_unread_message_indicator_when_message_is_read(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(is_read=True)
        )
        self.assertFalse(view_model.messages[0].show_unread_message_indicator)

    def test_show_unread_message_indicator_when_message_is_unread(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(is_read=False)
        )
        self.assertTrue(view_model.messages[0].show_unread_message_indicator)

    def test_correct_message_url_is_displayed_in_view_model(self) -> None:
        message_id = uuid4()
        expected_url = self.url_index.get_message_url(message_id)
        view_model = self.presenter.present(
            self._create_response_with_one_message(message_id=message_id)
        )
        self.assertEqual(expected_url, view_model.messages[0].message_url)

    def _create_response_with_one_message(
        self,
        title: str = "test title",
        sender_name: str = "sender name",
        is_read: bool = True,
        message_id: Optional[UUID] = None,
    ) -> ListMessagesResponse:
        if message_id is None:
            message_id = uuid4()
        return ListMessagesResponse(
            messages=[
                ListedMessage(
                    title=title,
                    sender_name=sender_name,
                    message_id=message_id,
                    is_read=is_read,
                )
            ]
        )


class FakeUrlIndex:
    def get_message_url(self, message_id: UUID) -> str:
        return f"url:{message_id}"
