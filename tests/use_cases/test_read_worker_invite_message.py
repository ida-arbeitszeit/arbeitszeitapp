from datetime import datetime
from typing import Callable, cast
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import Company, Member, WorkerInviteMessage
from arbeitszeit.use_cases import ReadWorkerInviteMessage
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector
from .repositories import WorkerInviteMessageRepository


class ReadWorkerInviteMessageTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.read_message = self.injector.get(ReadWorkerInviteMessage)
        self.worker_invite_message_repository = self.injector.get(
            WorkerInviteMessageRepository
        )
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.worker = self.member_generator.create_member()
        self.other_worker = self.member_generator.create_member()
        self.sender = self.company_generator.create_company()

    def test_reading_non_existing_message_as_non_existing_user_failes(self) -> None:
        response = self.read_message(
            ReadWorkerInviteMessage.Request(
                message_id=uuid4(),
                reader_id=uuid4(),
            )
        )
        self.assertIsInstance(
            response,
            ReadWorkerInviteMessage.Failure,
        )

    def test_trying_to_read_an_existing_message_for_existing_user_is_success(
        self,
    ) -> None:
        message = self._create_message()
        response = self.read_message(
            ReadWorkerInviteMessage.Request(
                reader_id=self.worker.id,
                message_id=message.id,
            )
        )
        self.assertIsInstance(
            response,
            ReadWorkerInviteMessage.Success,
        )

    def test_trying_to_read_a_non_existing_message_for_existing_user_is_a_failure(
        self,
    ) -> None:
        response = self.read_message(
            ReadWorkerInviteMessage.Request(
                reader_id=self.worker.id,
                message_id=uuid4(),
            )
        )
        self.assertIsInstance(
            response,
            ReadWorkerInviteMessage.Failure,
        )

    def test_trying_to_read_a_message_addressed_to_another_member_results_in_failure(
        self,
    ) -> None:
        message = self._create_message()
        response = self.read_message(
            ReadWorkerInviteMessage.Request(
                reader_id=self.other_worker.id,
                message_id=message.id,
            )
        )
        self.assertIsInstance(
            response,
            ReadWorkerInviteMessage.Failure,
        )

    def test_that_a_message_counts_as_being_read_after_the_user_reads_it(self) -> None:
        message = self._create_message()
        self.assertFalse(message.is_read)
        self.read_message(
            ReadWorkerInviteMessage.Request(
                reader_id=self.worker.id,
                message_id=message.id,
            )
        )
        self.assertTrue(message.is_read)

    def assertSuccess(
        self,
        response: ReadWorkerInviteMessage.Response,
        condition: Callable[[ReadWorkerInviteMessage.Success], bool],
    ) -> None:
        self.assertIsInstance(response, ReadWorkerInviteMessage.Success)
        self.assertTrue(condition(cast(ReadWorkerInviteMessage.Success, response)))

    def _create_message(
        self,
        invite_id: UUID = None,
        company: Company = None,
        worker: Member = None,
    ) -> WorkerInviteMessage:
        if invite_id is None:
            invite_id = uuid4()
        if company is None:
            company = self.sender
        if worker is None:
            worker = self.worker
        return self.worker_invite_message_repository.create_message(
            invite_id=invite_id,
            company=company,
            worker=worker,
            creation_date=datetime.now(),
        )
