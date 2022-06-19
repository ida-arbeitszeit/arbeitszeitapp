from typing import List, cast
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.repositories import MessageRepository
from arbeitszeit.use_cases import (
    AnswerCompanyWorkInvite,
    AnswerCompanyWorkInviteRequest,
    InviteWorkerToCompanyUseCase,
    ListedMessage,
    ListMessages,
    ListMessagesRequest,
    ReadMessage,
    ReadMessageRequest,
    ReadMessageSuccess,
)
from arbeitszeit.user_action import UserAction, UserActionType
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class InviteWorkerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.company = self.company_generator.create_company()
        self.member_generator = self.injector.get(MemberGenerator)
        self.member = self.member_generator.create_member()
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_can_successfully_invite_worker_which_was_not_previously_invited(
        self,
    ) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_twices(self) -> None:
        request = InviteWorkerToCompanyUseCase.Request(
            company=self.company.id,
            worker=self.member.id,
        )
        self.invite_worker_to_company(request)
        response = self.invite_worker_to_company(request)
        assert not response.is_success

    def test_can_invite_different_workers(self) -> None:
        first_member = self.member_generator.create_member()
        second_member = self.member_generator.create_member()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=first_member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=second_member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_can_invite_same_worker_to_different_companies(self) -> None:
        first_company = self.company_generator.create_company()
        second_company = self.company_generator.create_company()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=first_company.id,
                worker=self.member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=second_company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=uuid4(),
            )
        )
        self.assertFalse(response.is_success)

    def test_cannot_invite_worker_to_company_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=uuid4(),
                worker=self.member.id,
            )
        )
        self.assertFalse(response.is_success)

    def test_response_uuid_is_not_none_on_successful_invite(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.assertIsNotNone(response.invite_id)

    def test_after_being_invited_the_member_has_received_a_message_with_the_correct_title(
        self,
    ) -> None:
        message_repository: MessageRepository
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        message_repository = self.injector.get(MessageRepository)  # type: ignore
        messages = list(message_repository.get_messages_to_user(self.member.id))
        self.assertEqual(len(messages), 1)
        message = messages[0]
        self.assertEqual(
            message.title, f"Company {self.company.name} invited you to join them"
        )


class WorkInviteMessageTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)
        self.list_messages = self.injector.get(ListMessages)
        self.read_message = self.injector.get(ReadMessage)
        self.answer_invite = self.injector.get(AnswerCompanyWorkInvite)
        self.member = self.member_generator.create_member()
        self.company = self.company_generator.create_company()

    def test_inviting_a_worker_sends_them_a_message(self) -> None:
        self.assertMemberMessageCount(0)
        self.invite_member()
        self.assertMemberMessageCount(1)

    def test_message_received_is_unread(self) -> None:
        self.invite_member()
        message = self.get_member_messages()[0]
        self.assertFalse(message.is_read)

    def test_that_received_message_contains_a_user_action(self) -> None:
        self.invite_member()
        message_details = self.read_invite_message()
        self.assertIsNotNone(message_details.user_action)

    def test_that_received_message_action_type_is_properly_set(self) -> None:
        self.invite_member()
        message_details = self.read_invite_message()
        self.assertEqual(
            cast(UserAction, message_details.user_action).type,
            UserActionType.answer_invite,
        )

    def test_that_user_action_id_in_received_message_can_be_accepted(self) -> None:
        self.invite_member()
        message_details = self.read_invite_message()
        invite_id = cast(UserAction, message_details.user_action).reference
        self.assertCanAcceptInvite(invite_id)

    def assertCanAcceptInvite(self, invite_id: UUID) -> None:
        response = self.answer_invite(
            AnswerCompanyWorkInviteRequest(
                is_accepted=True, invite_id=invite_id, user=self.member.id
            )
        )
        self.assertTrue(response.is_success)

    def read_invite_message(self) -> ReadMessageSuccess:
        message = self.get_member_messages()[0]
        message_details = self.read_message(
            ReadMessageRequest(
                reader_id=self.member.id,
                message_id=message.message_id,
            )
        )
        assert isinstance(message_details, ReadMessageSuccess)
        return message_details

    def invite_member(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id, worker=self.member.id
            )
        )

    def assertMemberMessageCount(self, count: int) -> None:
        self.assertEqual(len(self.get_member_messages()), count)

    def get_member_messages(self) -> List[ListedMessage]:
        messages_response = self.list_messages(ListMessagesRequest(self.member.id))
        return messages_response.messages
