from typing import Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from tests.flask_integration.flask import LogInUser, ViewTestCase


class ShowTransferRequestBaseTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accept_coordination_transfer_use_case = self.injector.get(
            AcceptCoordinationTransferUseCase
        )

    def create_url(self, transfer_request: UUID) -> str:
        return f"/company/show_coordination_transfer_request/{transfer_request}"

    def create_transfer_request(
        self,
        requester_is_coordinator: bool = True,
        candidate_is_current_user: bool = True,
    ) -> UUID:
        coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = (
            self.get_current_user()
            if candidate_is_current_user
            else self.company_generator.create_company()
        )
        requester = (
            coordinator
            if requester_is_coordinator
            else self.company_generator.create_company()
        )
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester, cooperation=cooperation, candidate=candidate
        )
        return transfer_request

    def get_current_user(self) -> UUID:
        with self.client.session_transaction() as session:
            current_user: Optional[str] = session.get("_user_id")
        assert current_user, "No logged in user"
        return UUID(current_user)

    def accept_transfer_request(
        self, transfer_request: UUID, accepting_company: UUID
    ) -> None:
        response = (
            self.accept_coordination_transfer_use_case.accept_coordination_transfer(
                AcceptCoordinationTransferUseCase.Request(
                    transfer_request_id=transfer_request,
                    accepting_company=accepting_company,
                )
            )
        )
        assert not response.is_rejected


class NonCompanyGetRequestTests(ShowTransferRequestBaseTest):
    def setUp(self) -> None:
        super().setUp()

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.create_url(uuid4()),
            method="get",
            login=login,
            expected_code=expected_code,
        )


class CompanyGetRequestTests(ShowTransferRequestBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.user = self.login_company()

    def test_that_404_is_returned_if_transfer_request_does_not_exist(self) -> None:
        url = self.create_url(transfer_request=uuid4())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_that_200_is_returned_if_transfer_request_does_exist(self) -> None:
        transfer_request = self.create_transfer_request()
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_that_post_form_does_not_show_on_page_if_current_user_is_not_candidate(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(candidate_is_current_user=False)
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertNotIn('<form method="post">', response.text)

    def test_that_post_form_does_not_show_on_page_if_transfer_has_already_been_accepted(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request()
        self.accept_transfer_request(
            transfer_request=transfer_request, accepting_company=self.user.id
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertNotIn('<form method="post">', response.text)

    def test_that_post_form_does_show_on_page_if_transfer_has_not_been_accepted_and_current_user_is_candidate(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request()
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertIn('<form method="post">', response.text)


class CompanyPostRequestTests(ShowTransferRequestBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.user = self.login_company()

    def test_that_404_is_returned_if_transfer_request_does_not_exist(self) -> None:
        url = self.create_url(transfer_request=uuid4())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_that_302_is_returned_if_transfer_request_exists_and_user_is_candidate(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request()
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_that_403_is_returned_if_transfer_request_exists_but_candidate_is_not_current_user(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(candidate_is_current_user=False)
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_that_409_is_returned_if_transfer_request_exists_but_request_has_already_been_accepted(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request()
        self.accept_transfer_request(
            transfer_request=transfer_request, accepting_company=self.user.id
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 409)
