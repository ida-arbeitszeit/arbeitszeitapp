from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit.use_cases.show_work_invites import (
    ShowWorkInvites,
    ShowWorkInvitesRequest,
)

from .base_test_case import BaseTestCase


class ShowWorkInvitesTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.show_work_invites = self.injector.get(ShowWorkInvites)
        self.member = self.member_generator.create_member()
        self.company = self.company_generator.create_company_record().id
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_no_invites_are_shown_when_none_was_sent(self) -> None:
        request = ShowWorkInvitesRequest(member=self.member)
        response = self.show_work_invites(request)
        self.assertFalse(response.invites)

    def test_invites_are_shown_when_worker_was_previously_invited(self) -> None:
        self.invite_worker_to_company.invite_worker(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        response = self.show_work_invites(
            ShowWorkInvitesRequest(
                member=self.member,
            )
        )
        self.assertTrue(response.invites)

    def test_show_which_company_sent_the_invite(self) -> None:
        self.invite_worker_to_company.invite_worker(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        response = self.show_work_invites(
            ShowWorkInvitesRequest(
                member=self.member,
            )
        )
        self.assertEqual(response.invites[0].company_id, self.company)
