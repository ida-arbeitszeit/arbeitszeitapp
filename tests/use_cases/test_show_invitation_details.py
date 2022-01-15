from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases import (
    InviteWorkerToCompany,
    InviteWorkerToCompanyRequest,
    ShowInvitationDetailsRequest,
    ShowInvitationDetailsUseCase,
)

from ..data_generators import CompanyGenerator, MemberGenerator
from .dependency_injection import get_dependency_injector


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowInvitationDetailsUseCase)
        self.invite_worker_use_case = self.injector.get(InviteWorkerToCompany)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_use_case_is_unsuccessful_when_showing_details_for_non_exsting_invite_for_non_existing_user(
        self,
    ) -> None:
        request = ShowInvitationDetailsRequest(invite_id=uuid4(), user=uuid4())
        response = self.use_case.show_invitation_details(request)
        self.assertFalse(response.is_success)

    def test_that_use_case_is_successful_when_when_invite_and_user_exist_and_user_is_subject_of_the_invite(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        member = self.member_generator.create_member()
        invite_id = self.invite_worker(company=company.id, worker=member.id)
        request = ShowInvitationDetailsRequest(invite_id=invite_id, user=member.id)
        response = self.use_case.show_invitation_details(request)
        self.assertTrue(response.is_success)

    def test_that_use_case_fails_with_valid_invite_but_invalid_user(self) -> None:
        company = self.company_generator.create_company()
        member = self.member_generator.create_member()
        invite_id = self.invite_worker(company=company.id, worker=member.id)
        request = ShowInvitationDetailsRequest(invite_id=invite_id, user=uuid4())
        response = self.use_case.show_invitation_details(request)
        self.assertFalse(response.is_success)

    def test_that_use_case_fails_with_if_user_is_not_subject_of_invite(self) -> None:
        company = self.company_generator.create_company()
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        invite_id = self.invite_worker(company=company.id, worker=member.id)
        request = ShowInvitationDetailsRequest(
            invite_id=invite_id, user=other_member.id
        )
        response = self.use_case.show_invitation_details(request)
        self.assertFalse(response.is_success)

    def invite_worker(self, company: UUID, worker: UUID) -> UUID:
        invite_response = self.invite_worker_use_case(
            InviteWorkerToCompanyRequest(
                company=company,
                worker=worker,
            )
        )
        invite_id = invite_response.invite_id
        assert invite_id
        return invite_id
