from unittest import TestCase
from uuid import uuid4

from arbeitszeit import repositories as interfaces
from project.database.repositories import WorkerInviteRepository

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
        self.company = uuid4()
        self.worker = uuid4()

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
