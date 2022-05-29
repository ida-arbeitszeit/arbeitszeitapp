from datetime import datetime
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import ListMessages, ReadWorkerInviteMessage
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    WorkerInviteMessageGenerator,
)

from .dependency_injection import get_dependency_injector


class ListMessagesTest(TestCase):
    def setUp(self) -> None:
        injector = get_dependency_injector()
        self.list_messages = injector.get(ListMessages)
        self.message_generator = injector.get(WorkerInviteMessageGenerator)
        self.member_generator = injector.get(MemberGenerator)
        self.company_generator = injector.get(CompanyGenerator)
        self.read_message = injector.get(ReadWorkerInviteMessage)

    def test_message_list_for_non_existing_user_is_empty(self) -> None:
        response = self.list_messages(
            ListMessages.Request(
                user=uuid4(),
            )
        )
        self.assertFalse(response.worker_invite_messages)

    def test_worker_with_one_message_returns_messages_in_response(self) -> None:
        worker = self.member_generator.create_member()
        self.message_generator.create_message(worker=worker)
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertTrue(response.worker_invite_messages)

    def test_worker_with_two_messages_returns_two_messages_in_response(self) -> None:
        worker = self.member_generator.create_member()
        self.message_generator.create_message(worker=worker)
        self.message_generator.create_message(worker=worker)
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertEqual(len(response.worker_invite_messages), 2)

    def test_that_newly_created_messages_are_listed_as_unread(self) -> None:
        worker = self.member_generator.create_member()
        self.message_generator.create_message(worker=worker)
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertFalse(response.worker_invite_messages[0].is_read)

    def test_that_listed_messages_contain_timestamp(self) -> None:
        worker = self.member_generator.create_member()
        self.message_generator.create_message(worker=worker)
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertIsInstance(
            response.worker_invite_messages[0].creation_date, datetime
        )

    def test_that_listed_messages_contain_the_companys_name(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company()
        self.message_generator.create_message(company=company, worker=worker)
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertEqual(response.worker_invite_messages[0].company_name, company.name)

    def test_that_a_previously_read_message_is_listed_as_read(self) -> None:
        worker = self.member_generator.create_member()
        message = self.message_generator.create_message(worker=worker)
        self.read_message(ReadWorkerInviteMessage.Request(worker.id, message.id))
        response = self.list_messages(
            ListMessages.Request(
                user=worker.id,
            )
        )
        self.assertTrue(response.worker_invite_messages[0].is_read)
