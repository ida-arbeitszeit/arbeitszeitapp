from uuid import UUID

from parameterized import parameterized

from arbeitszeit.interactors import invite_worker_to_company, list_pending_work_invites
from tests.interactors.base_test_case import BaseTestCase


class ListPendingWorkInvitesTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            list_pending_work_invites.ListPendingWorkInvitesInteractor
        )

    def test_no_pending_invites_are_returned_if_no_invites_exist(self) -> None:
        company = self.company_generator.create_company()
        response = self.list_pending_invites(company=company)
        assert not response.pending_invites

    def test_no_pending_invites_are_returned_if_another_company_has_invited_members(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        worker = self.member_generator.create_member()
        self.invite_worker(company=other_company, worker=worker)
        response = self.list_pending_invites(company=company)
        assert not response.pending_invites

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_pending_invites_are_returned(self, count: int) -> None:
        company = self.company_generator.create_company()
        workers = [self.member_generator.create_member() for _ in range(count)]
        for worker in workers:
            self.invite_worker(company=company, worker=worker)
        response = self.list_pending_invites(company=company)
        assert len(response.pending_invites) == count

    def test_pending_invite_contains_member_id(self) -> None:
        company = self.company_generator.create_company()
        worker = self.member_generator.create_member()
        self.invite_worker(company=company, worker=worker)
        response = self.list_pending_invites(company=company)
        assert response.pending_invites[0].member_id == worker

    def test_pending_invite_contains_member_name(self) -> None:
        company = self.company_generator.create_company()
        MEMBER_NAME = "Jan Appel"
        worker = self.member_generator.create_member(name=MEMBER_NAME)
        self.invite_worker(company=company, worker=worker)
        response = self.list_pending_invites(company=company)
        assert response.pending_invites[0].member_name == MEMBER_NAME

    def invite_worker(self, company: UUID, worker: UUID) -> None:
        request = invite_worker_to_company.InviteWorkerToCompanyInteractor.Request(
            company=company, worker=worker
        )
        interactor = self.injector.get(
            invite_worker_to_company.InviteWorkerToCompanyInteractor
        )
        response = interactor.invite_worker(request=request)
        assert not response.rejection_reason

    def list_pending_invites(self, company: UUID) -> list_pending_work_invites.Response:
        request = list_pending_work_invites.Request(company=company)
        return self.interactor.list_pending_work_invites(request=request)
