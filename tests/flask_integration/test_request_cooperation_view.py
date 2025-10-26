from uuid import uuid4

from .base_test_case import ViewTestCase


class LoggedInMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()
        self.url = "/company/request_cooperation"

    def test_member_gets_redirected_when_trying_to_access_company_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class NotLoggedInCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/request_cooperation"

    def test_company_gets_302_status_when_not_logged_in(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class LoggedInCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.url = "/company/request_cooperation"

    def test_company_gets_200_status_when_opening_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_request_shows_truncated_plan_name_and_id_of_company_plan(self) -> None:
        product_name = "product test name"
        plan = self.plan_generator.create_plan(
            planner=self.company, product_name=product_name
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(product_name[:10], response.get_data(as_text=True))
        self.assertIn(str(plan)[:6], response.get_data(as_text=True))

    def test_get_request_shows_message_if_company_has_no_plans(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("No plans yet.", response.get_data(as_text=True))

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_posting_malformed_plan_id_data_results_in_400(
        self,
    ) -> None:
        response = self.client.post(
            self.url, data=dict(plan_id="no uuid", cooperation_id=str(uuid4()))
        )
        self.assertEqual(response.status_code, 400)

    def test_posting_malformed_coop_id_data_results_in_400(
        self,
    ) -> None:
        response = self.client.post(
            self.url, data=dict(plan_id=str(uuid4()), cooperation_id="no uuid")
        )
        self.assertEqual(response.status_code, 400)

    def test_error_message_shows_up_when_posting_malformed_coop_id_data(
        self,
    ) -> None:
        response = self.client.post(
            self.url, data=dict(plan_id=str(uuid4()), cooperation_id="no uuid")
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid cooperation ID.", response.get_data(as_text=True))

    def test_error_message_shows_up_when_posting_malformed_plan_id_data(
        self,
    ) -> None:
        response = self.client.post(
            self.url, data=dict(plan_id="no uuid", cooperation_id=str(uuid4()))
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid plan ID.", response.get_data(as_text=True))

    def test_posting_valid_data_results_in_200(
        self,
    ) -> None:
        response = self.client.post(
            self.url, data=dict(plan_id=str(uuid4()), cooperation_id=str(uuid4()))
        )
        self.assertEqual(response.status_code, 200)
