from typing import Callable, Optional, Union, cast
from unittest import TestCase
from uuid import uuid4

from hypothesis import given, strategies

from arbeitszeit.entities import Company, Member, Message
from arbeitszeit.repositories import MessageRepository
from arbeitszeit.use_cases import (
    ReadMessage,
    ReadMessageFailure,
    ReadMessageRequest,
    ReadMessageResponse,
    ReadMessageSuccess,
)
from arbeitszeit.user_action import UserAction
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class ReadMessageTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.read_message = self.injector.get(ReadMessage)
        self.member_generator = self.injector.get(MemberGenerator)
        self.message_repository = self.injector.get(MessageRepository)  # type: ignore
        self.addressee = self.member_generator.create_member()
        self.other_member = self.member_generator.create_member()
        self.sender = self.member_generator.create_member()

    def test_reading_non_existing_message_as_non_existing_user_failes(self) -> None:
        response = self.read_message(
            ReadMessageRequest(
                message_id=uuid4(),
                reader_id=uuid4(),
            )
        )
        self.assertIsInstance(
            response,
            ReadMessageFailure,
        )

    def test_trying_to_read_an_existing_message_for_existing_user_is_success(
        self,
    ) -> None:
        message = self._create_message()
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertIsInstance(
            response,
            ReadMessageSuccess,
        )

    def test_trying_to_read_a_non_existing_message_for_existing_user_is_a_failure(
        self,
    ) -> None:
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=uuid4(),
            )
        )
        self.assertIsInstance(
            response,
            ReadMessageFailure,
        )

    def test_trying_to_read_a_message_addressed_to_another_member_results_in_failure(
        self,
    ) -> None:
        message = self._create_message()
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.other_member.id,
                message_id=message.id,
            )
        )
        self.assertIsInstance(
            response,
            ReadMessageFailure,
        )

    def test_company_can_read_messages_that_are_addressed_to_it(self) -> None:
        company = self.injector.get(CompanyGenerator).create_company()
        message = self._create_message(addressee=company)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=company.id,
                message_id=message.id,
            )
        )
        self.assertIsInstance(
            response,
            ReadMessageSuccess,
        )

    @given(expected_title=strategies.text())
    def test_title_of_message_is_returned_as_stored(self, expected_title: str) -> None:
        message = self._create_message(title=expected_title)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertSuccess(response, lambda r: r.message_title == expected_title)

    @given(expected_content=strategies.text())
    def test_content_of_message_is_returned_as_stored(
        self, expected_content: str
    ) -> None:
        message = self._create_message(content=expected_content)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertSuccess(response, lambda r: r.message_content == expected_content)

    def test_sender_remarks_are_none_if_none_were_specified(self) -> None:
        message = self._create_message(sender_remarks=None)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertSuccess(response, lambda r: r.sender_remarks is None)

    @given(expected_remarks=strategies.text())
    def test_sender_remarks_are_as_specified_when_created(
        self, expected_remarks: str
    ) -> None:
        message = self._create_message(sender_remarks=expected_remarks)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertSuccess(response, lambda r: r.sender_remarks == expected_remarks)

    def test_user_action_is_none_then_response_shows_also_user_action_none(
        self,
    ) -> None:
        message = self._create_message(user_action=None)
        response = self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertSuccess(response, lambda r: r.user_action is None)

    def test_that_a_message_counts_as_being_read_after_the_user_reads_it(self) -> None:
        message = self._create_message()
        self.assertFalse(message.is_read)
        self.read_message(
            ReadMessageRequest(
                reader_id=self.addressee.id,
                message_id=message.id,
            )
        )
        self.assertTrue(message.is_read)

    def assertSuccess(
        self,
        response: ReadMessageResponse,
        condition: Callable[[ReadMessageSuccess], bool],
    ) -> None:
        self.assertIsInstance(response, ReadMessageSuccess)
        self.assertTrue(condition(cast(ReadMessageSuccess, response)))

    def _create_message(
        self,
        addressee: Union[None, Member, Company] = None,
        title: str = "test title",
        content: str = "test content",
        sender_remarks: Optional[str] = None,
        user_action: Optional[UserAction] = None,
    ) -> Message:
        if addressee is None:
            addressee = self.addressee
        return self.message_repository.create_message(
            sender=self.sender,
            addressee=addressee,
            title=title,
            content=content,
            sender_remarks=sender_remarks,
            reference=user_action,
        )
