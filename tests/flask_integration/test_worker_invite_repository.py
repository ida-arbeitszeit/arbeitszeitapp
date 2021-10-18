from unittest import TestCase
from uuid import uuid4

from arbeitszeit import repositories as interfaces
from project.database.repositories import WorkerInviteRepository
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class WorkerInviteRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repository = self.injector.get(WorkerInviteRepository)
        self.company = uuid4()
        self.worker = uuid4()

    def test_companies_a_member_is_invited_to_is_empty_with_no_invites_sent(
        self,
    ) -> None:
        self.assertFalse(
            list(self.repository.get_companies_worker_is_invited_to(self.worker))
        )

    def test_company_shows_up_in_invites_for_member(self) -> None:
        self.repository.create_company_worker_invite(self.company, self.worker)
        self.assertEqual(
            [self.company],
            list(self.repository.get_companies_worker_is_invited_to(self.worker)),
        )

    def test_that_company_does_not_show_in_invites_for_other_member(self) -> None:
        other_member = uuid4()
        self.repository.create_company_worker_invite(self.company, self.worker)
        self.assertFalse(
            list(self.repository.get_companies_worker_is_invited_to(other_member)),
        )

    def test_that_we_get_production_instance_of_repository_from_dependency_injection(
        self,
    ) -> None:
        repository = self.injector.get(interfaces.WorkerInviteRepository)
        self.assertIsInstance(repository, WorkerInviteRepository)


class IsWorkerInvitedToCompanyTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repository = self.injector.get(WorkerInviteRepository)
        company_generator = self.injector.get(CompanyGenerator)
        member_generator = self.injector.get(MemberGenerator)
        self.company = company_generator.create_company().id
        self.worker = member_generator.create_member().id

    def test_being_invited_to_a_company_does_not_invite_worker_to_other_company(
        self,
    ) -> None:
        self.repository.create_company_worker_invite(self.company, self.worker)
        other_company = uuid4()
        self.assertFalse(
            self.repository.is_worker_invited_to_company(
                other_company,
                self.worker,
            )
        )

    def test_worker_is_not_invited_with_non_existent_company_and_member(self) -> None:
        self.assertFalse(
            self.repository.is_worker_invited_to_company(self.company, self.worker)
        )

    def test_after_creating_an_invite_a_member_counts_as_invited(self) -> None:
        self.repository.create_company_worker_invite(self.company, self.worker)
        self.assertTrue(
            self.repository.is_worker_invited_to_company(self.company, self.worker)
        )

    def test_get_by_id_returns_invite_if_one_was_created_before(self) -> None:
        invite_id = self.repository.create_company_worker_invite(
            self.company, self.worker
        )
        invite = self.repository.get_by_id(invite_id)
        self.assertIsNotNone(invite)

    def test_get_by_id_returns_no_invite_if_random_uuid_is_queried(self) -> None:
        invite = self.repository.get_by_id(uuid4())
        self.assertIsNone(invite)

    def test_get_by_id_returns_invite_with_correct_attributes(self) -> None:
        invite_id = self.repository.create_company_worker_invite(
            self.company, self.worker
        )
        invite = self.repository.get_by_id(invite_id)
        assert invite is not None
        self.assertEqual(invite.company.id, self.company)
        self.assertEqual(invite.member.id, self.worker)

    def test_invite_cannot_be_retrieved_after_deletion(self) -> None:
        invite_id = self.repository.create_company_worker_invite(
            self.company, self.worker
        )
        self.repository.delete_invite(invite_id)
        self.assertIsNone(self.repository.get_by_id(invite_id))

    def test_deleting_a_non_existing_invite_does_not_raise(self) -> None:
        self.repository.delete_invite(uuid4())
