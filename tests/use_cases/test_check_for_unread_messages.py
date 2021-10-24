from unittest import TestCase
from uuid import uuid4

from arbeitszeit.repositories import MessageRepository
from arbeitszeit.use_cases import (
    CheckForUnreadMessages,
    CheckForUnreadMessagesRequest,
    ReadMessage,
    ReadMessageRequest,
)
from tests.data_generators import MemberGenerator

from .dependency_injection import get_dependency_injector


class CheckForUnreadMessagesTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.check_for_unread_messages = self.injector.get(CheckForUnreadMessages)

    def test_non_existing_users_are_not_considered_to_have_unread_messages(
        self,
    ) -> None:
        response = self.check_for_unread_messages(
            CheckForUnreadMessagesRequest(
                user=uuid4(),
            )
        )
        self.assertFalse(response.has_unread_messages)

    def test_user_has_no_unread_messages_after_one_was_created_and_read(self) -> None:
        message_repo = self.injector.get(MessageRepository)  # type: ignore
        member_generator = self.injector.get(MemberGenerator)
        sender = member_generator.create_member()
        addressee = member_generator.create_member()
        read_message = self.injector.get(ReadMessage)
        message = message_repo.create_message(
            sender=sender,
            addressee=addressee,
            title="test title",
            content="test content",
            sender_remarks=None,
            reference=None,
        )
        read_message(
            ReadMessageRequest(
                reader_id=addressee.id,
                message_id=message.id,
            )
        )
        response = self.check_for_unread_messages(
            CheckForUnreadMessagesRequest(
                user=addressee.id,
            )
        )
        self.assertFalse(response.has_unread_messages)
