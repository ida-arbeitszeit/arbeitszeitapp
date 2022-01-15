from uuid import uuid4

from arbeitszeit.use_cases import InviteWorkerToCompany, InviteWorkerToCompanyRequest
from tests.data_generators import CompanyGenerator

from .flask import ViewTestCase


class MemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member, _, self.email = self.login_member()
        self.member = self.confirm_member(member=self.member, email=self.email)

    def test_when__member_requests_for_existing_invite_return_200_status(self) -> None:
        company_generator = self.injector.get(CompanyGenerator)
        invite_worker = self.injector.get(InviteWorkerToCompany)
        company = company_generator.create_company()
        use_case_response = invite_worker(
            InviteWorkerToCompanyRequest(company.id, self.member.id)
        )
        http_response = self.client.get(
            f"/member/answer_invite/{use_case_response.invite_id}"
        )
        self.assertEqual(http_response.status_code, 200)

    def test_when_member_requests_for_non_existing_invite_return_404_status(
        self,
    ) -> None:
        http_response = self.client.get(f"/member/answer_invite/{uuid4()}")
        self.assertEqual(http_response.status_code, 404)

    def test_when_member_requests_for_invitation_meant_for_another_member_then_return_403_forbidden(
        self,
    ) -> None:
        company_generator = self.injector.get(CompanyGenerator)
        other_member = self.member_generator.create_member()
        invite_worker = self.injector.get(InviteWorkerToCompany)
        company = company_generator.create_company()
        use_case_response = invite_worker(
            InviteWorkerToCompanyRequest(company.id, other_member.id)
        )
        http_response = self.client.get(
            f"/member/answer_invite/{use_case_response.invite_id}"
        )
        self.assertEqual(http_response.status_code, 403)
