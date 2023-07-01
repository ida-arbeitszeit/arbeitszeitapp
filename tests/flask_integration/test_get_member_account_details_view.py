from .flask import ViewTestCase


class GetMemberAccountDetailsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/member/account"

    def test_that_logged_in_member_receives_200(self) -> None:
        self.login_member()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_that_response_contains_user_id(self) -> None:
        member = str(self.login_member().id)
        response = self.client.get(self.url)
        assert member in response.text
