from uuid import UUID, uuid4

from parameterized import parameterized

from tests.flask_integration.base_test_case import LogInUser, ViewTestCase


class ListPendingInvitesTestCase(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/list_pending_work_invites"

    def invite_worker(self, worker_id: UUID) -> None:
        url = "/company/invite_worker_to_company"
        self.client.post(
            url,
            data={"worker_id": worker_id},
        )


class GetTests(ListPendingInvitesTestCase):
    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_logged_in_users_get_expected_status_codes(
        self, login: LogInUser | None, expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_unauthenticated_users_get_302(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=None,
            expected_code=302,
        )

    def test_company_gets_200_when_it_has_one_pending_invite(self) -> None:
        self.login_company()
        worker_id = self.member_generator.create_member()
        self.invite_worker(worker_id)
        response = self.client.get(self.url)
        assert response.status_code == 200


class PostTests(ListPendingInvitesTestCase):
    def test_that_resending_invite_to_unexisting_worker_returns_400(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="post",
            login=LogInUser.company,
            expected_code=400,
            data={"worker_id": uuid4()},
        )

    def test_that_resending_invite_to_existing_worker_that_has_been_invited_returns_302(
        self,
    ) -> None:
        self.login_company()
        worker_id = self.member_generator.create_member()
        self.invite_worker(worker_id)
        response = self.client.post(
            self.url,
            data={"worker_id": worker_id},
        )
        assert response.status_code == 302
