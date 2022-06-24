from unittest import TestCase

from arbeitszeit.use_cases import (
    InviteWorkerToCompanyUseCase,
    ShowWorkInvites,
    ShowWorkInvitesRequest,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class ShowWorkInvitesTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.show_work_invites = self.injector.get(ShowWorkInvites)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member = self.member_generator.create_member()
        self.company = self.company_generator.create_company()
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_no_invites_are_shown_when_none_was_sent(self) -> None:
        request = ShowWorkInvitesRequest(member=self.member.id)
        response = self.show_work_invites(request)
        self.assertFalse(response.invites)

    def test_invites_are_shown_when_worker_was_previously_invited(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        response = self.show_work_invites(
            ShowWorkInvitesRequest(
                member=self.member.id,
            )
        )
        self.assertTrue(response.invites)

    def test_show_which_company_sent_the_invite(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        response = self.show_work_invites(
            ShowWorkInvitesRequest(
                member=self.member.id,
            )
        )
        self.assertEqual(response.invites[0].company_id, self.company.id)
