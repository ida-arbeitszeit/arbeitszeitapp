from datetime import datetime
from unittest import TestCase
from uuid import UUID, uuid4

from hypothesis import given, strategies

from arbeitszeit.use_cases import ListMessages
from arbeitszeit_web.list_messages import ListMessagesPresenter
from tests.datetime_service import FakeDatetimeService
from tests.presenters.url_index import WorkInviteMessageUrlIndexImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class ListMessagesPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ListMessagesPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.url_index = self.injector.get(WorkInviteMessageUrlIndexImpl)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_view_model_contains_no_messages_when_non_were_provided(self) -> None:
        response = ListMessages.Response(worker_invite_messages=[])
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.worker_invite_messages)

    def test_view_model_contains_messages_when_one_was_provided(self) -> None:
        response = self._create_response_with_one_message()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.worker_invite_messages)

    @given(sender_name=strategies.text())
    def test_sender_name_is_propagated_into_title_of_view_model(
        self, sender_name: str
    ) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(company_name=sender_name)
        )
        self.assertIn(sender_name, view_model.worker_invite_messages[0].title)

    def test_dont_show_unread_message_indicator_when_message_is_read(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(is_read=True)
        )
        self.assertFalse(
            view_model.worker_invite_messages[0].show_unread_message_indicator
        )

    def test_show_unread_message_indicator_when_message_is_unread(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_message(is_read=False)
        )
        self.assertTrue(
            view_model.worker_invite_messages[0].show_unread_message_indicator
        )

    def test_correct_message_url_is_displayed_in_view_model(self) -> None:
        message_id = uuid4()
        expected_url = self.url_index.get_work_invite_message_url(message_id)
        view_model = self.presenter.present(
            self._create_response_with_one_message(message_id=message_id)
        )
        self.assertEqual(expected_url, view_model.worker_invite_messages[0].url)

    def test_message_creation_date_is_formatted_correctly_in_view_model(self) -> None:
        frozen_time = datetime.now()
        self.datetime_service.freeze_time(frozen_time)
        view_model = self.presenter.present(
            self._create_response_with_one_message(creation_date=frozen_time)
        )
        self.assertEqual(
            self.datetime_service.format_datetime(
                frozen_time, zone="Europe/Berlin", fmt="%d.%m."
            ),
            view_model.worker_invite_messages[0].creation_date,
        )

    def _create_response_with_one_message(
        self,
        message_id: UUID = uuid4(),
        company_name: str = "test name",
        is_read: bool = False,
        creation_date: datetime = None,
    ) -> ListMessages.Response:
        if creation_date is None:
            creation_date = self.datetime_service.now()
        return ListMessages.Response(
            worker_invite_messages=[
                ListMessages.InviteMessage(
                    message_id=message_id,
                    company_name=company_name,
                    is_read=is_read,
                    creation_date=creation_date,
                )
            ]
        )
