from .base_test_case import ViewTestCase


class ListTransfersTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/user/transfers"

    def test_that_logged_in_member_gets_200(self) -> None:
        self.login_member()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_that_logged_in_member_gets_200_when_transfers_exist(self) -> None:
        self.login_member()
        self.plan_generator.create_plan(approved=True)
        response = self.client.get(self.url)
        assert response.status_code == 200
