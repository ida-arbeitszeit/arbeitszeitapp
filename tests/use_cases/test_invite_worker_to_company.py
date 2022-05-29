from datetime import datetime
from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.repositories import WorkerInviteMessageRepository
from arbeitszeit.use_cases import (
    AnswerCompanyWorkInvite,
    InviteWorkerToCompanyUseCase,
    ListMessages,
    ReadWorkerInviteMessage,
)
from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.datetime_service import FakeDatetimeService

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

    def test_after_being_invited_the_member_has_received_a_message(
        self,
    ) -> None:
        message_repository: WorkerInviteMessageRepository
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        message_repository = self.injector.get(WorkerInviteMessageRepository)  # type: ignore
        messages = list(message_repository.get_messages_to_user(self.member.id))
        self.assertEqual(len(messages), 1)


class WorkInviteMessageTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)
        self.list_messages = self.injector.get(ListMessages)
        self.read_message = self.injector.get(ReadWorkerInviteMessage)
        self.answer_invite = self.injector.get(AnswerCompanyWorkInvite)
        self.member = self.member_generator.create_member()
        self.company = self.company_generator.create_company()
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_inviting_a_worker_sends_them_a_message(self) -> None:
        self.assertMemberMessageCount(0)
        self.invite_member()
        self.assertMemberMessageCount(1)

    def test_message_received_is_unread(self) -> None:
        self.invite_member()
        message = self.get_member_messages()[0]
        self.assertFalse(message.is_read)

    def test_message_received_has_current_timestamp(self) -> None:
        frozen_time = datetime(2022, 5, 29)
        self.datetime_service.freeze_time(frozen_time)
        self.invite_member()
        message = self.get_member_messages()[0]
        self.assertEqual(message.creation_date, frozen_time)

    def invite_member(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id, worker=self.member.id
            )
        )

    def assertMemberMessageCount(self, count: int) -> None:
        self.assertEqual(len(self.get_member_messages()), count)

    def get_member_messages(self) -> List[ListMessages.InviteMessage]:
        messages_response = self.list_messages(ListMessages.Request(self.member.id))
        return messages_response.worker_invite_messages
