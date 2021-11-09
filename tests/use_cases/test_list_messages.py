from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import (
    ListMessages,
    ListMessagesRequest,
    ReadMessage,
    ReadMessageRequest,
)
from tests.data_generators import CompanyGenerator, MemberGenerator, MessageGenerator

from .dependency_injection import get_dependency_injector


class ListMessagesTest(TestCase):
    def setUp(self) -> None:
        injector = get_dependency_injector()
        self.list_messages = injector.get(ListMessages)
        self.message_generator = injector.get(MessageGenerator)
        self.member_generator = injector.get(MemberGenerator)
        self.company_generator = injector.get(CompanyGenerator)
        self.read_message = injector.get(ReadMessage)

    def test_message_list_for_non_existing_user_is_empty(self) -> None:
        response = self.list_messages(
            ListMessagesRequest(
                user=uuid4(),
            )
        )
        self.assertFalse(response.messages)

    def test_member_with_one_message_returns_messages_in_response(self) -> None:
        user = self.member_generator.create_member()
        self.message_generator.create_message(addressee=user)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertTrue(response.messages)

    def test_company_with_one_message_returns_messages_in_response(self) -> None:
        user = self.company_generator.create_company()
        self.message_generator.create_message(addressee=user)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertTrue(response.messages)

    def test_member_with_two_messages_returns_two_messages_in_response(self) -> None:
        user = self.member_generator.create_member()
        self.message_generator.create_message(addressee=user)
        self.message_generator.create_message(addressee=user)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertEqual(len(response.messages), 2)

    def test_message_title_created_is_passed_to_response(self) -> None:
        expected_title = "test title 81742"
        user = self.member_generator.create_member()
        self.message_generator.create_message(addressee=user, title=expected_title)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertEqual(response.messages[0].title, expected_title)

    def test_message_sender_is_passed_to_response(self) -> None:
        expected_name = "test member name"
        sender = self.member_generator.create_member(name=expected_name)
        user = self.member_generator.create_member()
        self.message_generator.create_message(addressee=user, sender=sender)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertEqual(response.messages[0].sender_name, expected_name)

    def test_correct_message_id_is_in_response(self) -> None:
        user = self.company_generator.create_company()
        message = self.message_generator.create_message(addressee=user)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertTrue(response.messages[0].message_id, message.id)

    def test_that_newly_created_messages_are_listed_as_unread(self) -> None:
        user = self.company_generator.create_company()
        self.message_generator.create_message(addressee=user)
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertFalse(response.messages[0].is_read)

    def test_that_a_previously_read_message_is_listed_as_read(self) -> None:
        user = self.company_generator.create_company()
        message = self.message_generator.create_message(addressee=user)
        self.read_message(ReadMessageRequest(user.id, message.id))
        response = self.list_messages(
            ListMessagesRequest(
                user=user.id,
            )
        )
        self.assertTrue(response.messages[0].is_read)
