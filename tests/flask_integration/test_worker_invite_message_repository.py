from datetime import datetime
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit import repositories as interfaces
from arbeitszeit.entities import Company, Member, WorkerInviteMessage
from arbeitszeit.use_cases.read_worker_invite_message import ReadWorkerInviteMessage
from arbeitszeit_flask.database.repositories import WorkerInviteMessageRepository
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class WorkerInviteMessageRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repo: WorkerInviteMessageRepository = self.injector.get(
            interfaces.WorkerInviteMessageRepository
        )
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.worker = self.member_generator.create_member()
        self.company = self.company_generator.create_company()
        self.read_message_use_case = self.injector.get(ReadWorkerInviteMessage)

    def test_dependency_injection_returns_correct_type(self) -> None:
        repo = self.injector.get(interfaces.WorkerInviteMessageRepository)
        self.assertIsInstance(repo, WorkerInviteMessageRepository)

    def test_when_creating_a_message_it_can_be_retrieved_later_by_its_id(self) -> None:
        expected_message = self._create_message()
        self.assertEqual(
            expected_message,
            self.repo.get_by_id(expected_message.id),
        )

    def test_invite_id_is_stored_correctly(
        self,
    ) -> None:
        expected_invite_id = uuid4()
        message = self._create_message(
            invite_id=expected_invite_id,
        )
        self.assertEqual(
            message.invite_id,
            expected_invite_id,
        )

    def test_company_is_stored_correctly(
        self,
    ) -> None:
        message = self._create_message(
            company=self.company,
        )
        self.assertEqual(
            message.company,
            self.company,
        )

    def test_worker_is_stored_correctly(
        self,
    ) -> None:
        message = self._create_message(
            worker=self.worker,
        )
        self.assertEqual(
            message.worker,
            self.worker,
        )

    def test_creation_date_is_stored(
        self,
    ) -> None:
        message = self._create_message()
        self.assertIsInstance(message.creation_date, datetime)

    def test_no_user_messages_are_retrieved_when_none_were_created(self) -> None:
        messages = list(self.repo.get_messages_to_user(self.worker.id))
        self.assertFalse(messages)

    def test_one_user_message_is_retrieved_if_one_was_created_for_user(self) -> None:
        self._create_message()
        messages = list(self.repo.get_messages_to_user(self.worker.id))
        self.assertEqual(len(messages), 1)

    def test_no_messages_are_retrieved_when_one_was_created_for_other_user(
        self,
    ) -> None:
        other_worker = self.member_generator.create_member()
        self._create_message(worker=other_worker)
        messages = list(self.repo.get_messages_to_user(self.worker.id))
        self.assertFalse(messages)

    def test_that_message_can_be_marked_as_read(self) -> None:
        message = self._create_message()
        self.assertFalse(message.is_read)
        self.repo.mark_as_read(message)
        self.assertTrue(message.is_read)

    def test_marking_a_message_as_read_is_persisted(self) -> None:
        message = self._create_message()
        self.repo.mark_as_read(message)
        message_from_db = self.repo.get_by_id(message.id)
        assert message_from_db
        self.assertTrue(message_from_db.is_read)

    def test_after_creating_new_message_there_has_unread_messages_for_user_is_true(
        self,
    ) -> None:
        self._create_message()
        self.assertTrue(self.repo.has_unread_messages_for_user(self.worker.id))

    def test_without_any_message_there_are_no_unread_messages(self) -> None:
        self.assertFalse(self.repo.has_unread_messages_for_user(self.worker.id))

    def test_after_reading_the_only_message_there_are_no_unread_messages_left(
        self,
    ) -> None:
        message = self._create_message()
        self.read_message_use_case(
            ReadWorkerInviteMessage.Request(
                reader_id=self.worker.id,
                message_id=message.id,
            )
        )
        self.assertFalse(self.repo.has_unread_messages_for_user(self.worker.id))

    def test_no_message_retrieved_by_invite_when_there_is_none(self) -> None:
        retrieved_message = self.repo.get_by_invite(uuid4())
        self.assertIsNone(retrieved_message)

    def test_possible_to_retrieve_message_by_invite(self) -> None:
        invite_id = uuid4()
        expected_message = self._create_message(invite_id=invite_id)
        retrieved_message = self.repo.get_by_invite(invite_id)
        assert retrieved_message
        self.assertEqual(expected_message.id, retrieved_message.id)

    def test_only_one_message_gets_deleted(self) -> None:
        message_to_delete = self._create_message(worker=self.worker)
        self._create_message(worker=self.worker)
        self.assertEqual(len(list(self.repo.get_messages_to_user(self.worker.id))), 2)
        self.repo.delete_message(message_to_delete.id)
        self.assertEqual(len(list(self.repo.get_messages_to_user(self.worker.id))), 1)

    def test_correct_message_gets_deleted(self) -> None:
        message_to_delete = self._create_message(worker=self.worker)
        message_to_keep = self._create_message(worker=self.worker)
        self.assertEqual(len(list(self.repo.get_messages_to_user(self.worker.id))), 2)
        self.repo.delete_message(message_to_delete.id)
        messages_to_user = list(self.repo.get_messages_to_user(self.worker.id))
        self.assertIn(message_to_keep, messages_to_user)
        self.assertNotIn(message_to_delete, messages_to_user)

    def _create_message(
        self,
        invite_id: UUID = None,
        company: Company = None,
        worker: Member = None,
    ) -> WorkerInviteMessage:
        if invite_id is None:
            invite_id = uuid4()
        if company is None:
            company = self.company
        if worker is None:
            worker = self.worker
        return self.repo.create_message(
            invite_id=invite_id,
            company=company,
            worker=worker,
            creation_date=datetime.now(),
        )
