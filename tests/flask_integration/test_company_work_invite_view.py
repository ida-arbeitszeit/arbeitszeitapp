from uuid import UUID, uuid4

from arbeitszeit.use_cases import InviteWorkerToCompanyUseCase
from tests.data_generators import CompanyGenerator

from .flask import ViewTestCase


class AuthenticatedTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member(confirm_member=True)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_use_case = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_get_request_for_existing_invite_yields_status_200(self) -> None:
        invite_id = self.invite_member()
        response = self.client.get(self.get_url(invite_id))
        self.assertEqual(response.status_code, 200)

    def test_get_request_for_non_exiting_invite_yeilds_status_404(self) -> None:
        response = self.client.get(self.get_url(uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_when_posting_against_the_view_without_an_invite_get_302(self) -> None:
        response = self.client.post(self.get_url(uuid4()))
        self.assertEqual(response.status_code, 302)

    def test_when_posting_against_the_view_with_an_invite_get_302(self) -> None:
        response = self.client.post(self.get_url(self.invite_member()))
        self.assertEqual(response.status_code, 302)

    def get_url(self, invite_id: UUID) -> str:
        return f"/member/invite_details/{invite_id}"

    def invite_member(self) -> UUID:
        company = self.company_generator.create_company()
        response = self.invite_use_case(
            InviteWorkerToCompanyUseCase.Request(
                company.id,
                self.member.id,
            )
        )
        return response.invite_id
