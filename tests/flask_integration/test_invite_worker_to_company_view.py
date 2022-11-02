from tests.company import CompanyManager

from .flask import ViewTestCase


class AnonymousUserTests(ViewTestCase):
    def test_get_redirected_when_no_logged_in(self) -> None:
        response = self.client.get("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 302)


class InviteWorkerToCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.company_manager = self.injector.get(CompanyManager)

    def test_get_200_when_logged_in_as_company(self) -> None:
        response = self.client.get("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 200)

    def test_that_get_response_contains_worker_names(self) -> None:
        expected_member_name = "test member 123"
        worker = self.member_generator.create_member_entity(name=expected_member_name)
        self.company_manager.add_worker_to_company(self.company.id, worker.id)
        response = self.client.get("/company/invite_worker_to_company")
        self.assertIn(expected_member_name, response.data.decode("utf-8"))

    def test_post_yields_400_if_no_post_data_was_provided(self) -> None:
        response = self.client.post("/company/invite_worker_to_company")
        self.assertEqual(response.status_code, 400)

    def test_post_yields_200_if_correct_data_was_provided(self) -> None:
        member = self.member_generator.create_member_entity()
        response = self.client.post(
            "/company/invite_worker_to_company", data={"member_id": str(member.id)}
        )
        self.assertEqual(response.status_code, 200)

    def test_post_yields_400_with_incorrect_uuid(self) -> None:
        response = self.client.post(
            "/company/invite_worker_to_company", data={"member_id": "abc"}
        )
        self.assertEqual(response.status_code, 400)
