from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import CheckForUnreadMessages
from arbeitszeit.use_cases.read_worker_invite_message import ReadWorkerInviteMessage
from tests.data_generators import MemberGenerator, WorkerInviteMessageGenerator

from .dependency_injection import get_dependency_injector


class CheckForUnreadMessagesTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.check_for_unread_messages = self.injector.get(CheckForUnreadMessages)
        self.read_message_use_case = self.injector.get(ReadWorkerInviteMessage)
        self.member_generator = self.injector.get(MemberGenerator)
        self.worker_invite_message_generator = self.injector.get(
            WorkerInviteMessageGenerator
        )

    def test_non_existing_users_are_not_considered_to_have_unread_messages(
        self,
    ) -> None:
        response = self.check_for_unread_messages(
            CheckForUnreadMessages.Request(
                user=uuid4(),
            )
        )
        self.assertFalse(response.has_unread_messages)

    def test_user_has_unread_messages_after_one_worker_invite_message_was_created(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        self.worker_invite_message_generator.create_message(worker=worker)
        response = self.check_for_unread_messages(
            CheckForUnreadMessages.Request(
                user=worker.id,
            )
        )
        self.assertTrue(response.has_unread_messages)

    def test_user_has_no_unread_messages_after_one_worker_invite_message_was_created_for_another_worker(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        another_worker = self.member_generator.create_member()
        self.worker_invite_message_generator.create_message(worker=another_worker)
        response = self.check_for_unread_messages(
            CheckForUnreadMessages.Request(
                user=worker.id,
            )
        )
        self.assertFalse(response.has_unread_messages)

    def test_user_has_no_unread_messages_after_one_worker_invite_message_was_created_and_read(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        invite_message = self.worker_invite_message_generator.create_message(
            worker=worker
        )
        self.read_message_use_case(
            ReadWorkerInviteMessage.Request(
                reader_id=worker.id,
                message_id=invite_message.id,
            )
        )
        response = self.check_for_unread_messages(
            CheckForUnreadMessages.Request(
                user=worker.id,
            )
        )
        self.assertFalse(response.has_unread_messages)
