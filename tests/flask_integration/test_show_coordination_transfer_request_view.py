from typing import Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors.accept_coordination_transfer import (
    AcceptCoordinationTransferInteractor,
)
from tests.flask_integration.flask import LogInUser, ViewTestCase


class ShowTransferRequestBaseTest(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accept_coordination_transfer_interactor = self.injector.get(
            AcceptCoordinationTransferInteractor
        )

    def create_url(self, transfer_request: UUID) -> str:
        return f"/company/show_coordination_transfer_request/{transfer_request}"

    def create_transfer_request(
        self,
        *,
        candidate: UUID,
        requester: Optional[UUID] = None,
    ) -> UUID:
        coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        requester = requester or coordinator
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester, cooperation=cooperation, candidate=candidate
        )
        return transfer_request

    def accept_transfer_request(
        self, transfer_request: UUID, accepting_company: UUID
    ) -> None:
        response = (
            self.accept_coordination_transfer_interactor.accept_coordination_transfer(
                AcceptCoordinationTransferInteractor.Request(
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
        transfer_request = self.create_transfer_request(candidate=self.user)
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_that_post_form_does_not_show_on_page_if_current_user_is_not_candidate(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(
            candidate=self.company_generator.create_company()
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertNotIn('<form method="post">', response.text)

    def test_that_post_form_does_not_show_on_page_if_transfer_has_already_been_accepted(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(candidate=self.user)
        self.accept_transfer_request(
            transfer_request=transfer_request, accepting_company=self.user
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.get(url)
        self.assertNotIn('<form method="post">', response.text)

    def test_that_post_form_does_show_on_page_if_transfer_has_not_been_accepted_and_current_user_is_candidate(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(candidate=self.user)
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
        transfer_request = self.create_transfer_request(candidate=self.user)
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_that_403_is_returned_if_transfer_request_exists_but_candidate_is_not_current_user(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(
            candidate=self.company_generator.create_company()
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_that_409_is_returned_if_transfer_request_exists_but_request_has_already_been_accepted(
        self,
    ) -> None:
        transfer_request = self.create_transfer_request(candidate=self.user)
        self.accept_transfer_request(
            transfer_request=transfer_request, accepting_company=self.user
        )
        url = self.create_url(transfer_request=transfer_request)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 409)
