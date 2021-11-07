from .view import ViewTestCase


class InviteWorkerToCompanyTests(ViewTestCase):
    def test_get_redirected_when_no_logged_in(self) -> None:
        response = self.client.get("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 302)

    def test_get_200_when_logged_in_as_company(self) -> None:
        self.login_company()
        response = self.client.get("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 200)

    def test_post_yields_400_if_no_post_data_was_provided(self) -> None:
        self.login_company()
        response = self.client.post("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 400)

    def test_post_yields_200_if_correct_data_was_provided(self) -> None:
        member = self.member_generator.create_member()
        self.login_company()
        response = self.client.post(
            "/company/invite_worker_to_company", data={"member_id": str(member.id)}
        )
        self.assertEqual(response.status_code, 200)

    def test_post_yields_400_with_incorrect_uuid(self) -> None:
        self.login_company()
        response = self.client.post(
            "/company/invite_worker_to_company", data={"member_id": "abc"}
        )
        self.assertEqual(response.status_code, 400)
