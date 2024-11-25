from uuid import uuid4

from .flask import ViewTestCase


class CompanyGetTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_that_logged_in_company_get_200_response(self) -> None:
        response = self.client.get("/company/register_productive_consumption")
        self.assertEqual(response.status_code, 200)

    def test_that_company_receives_error_code_if_plan_id_is_not_a_valid_uuid(
        self,
    ) -> None:
        response = self.client.get(
            "/company/register_productive_consumption?plan_id=invalid_uuid"
        )
        assert response.status_code >= 400

    def test_that_company_receives_error_code_if_amount_is_not_a_valid_number(
        self,
    ) -> None:
        response = self.client.get(
            "/company/register_productive_consumption?amount=invalid_number"
        )
        assert response.status_code >= 400

    def test_that_company_receives_error_code_if_type_of_consumption_is_invalid(
        self,
    ) -> None:
        response = self.client.get(
            "/company/register_productive_consumption?type_of_consumption=invalid"
        )
        assert response.status_code >= 400

    def test_that_select_button_is_present_in_response_html_if_no_plan_id_is_given(
        self,
    ) -> None:
        response = self.client.get("/company/register_productive_consumption")
        assert ">Select</button>" in response.text

    def test_that_register_and_cancel_buttons_are_present_in_response_html_if_plan_id_is_given(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        response = self.client.get(
            f"/company/register_productive_consumption?plan_id={plan}"
        )
        assert ">Register</button>" in response.text
        assert ">Cancel</a>" in response.text

    def test_that_form_has_get_method_if_no_plan_id_is_given(self) -> None:
        response = self.client.get("/company/register_productive_consumption")
        assert '<form method="get"' in response.text
        assert '<form method="post"' not in response.text

    def test_that_form_has_post_method_if_plan_id_is_given(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.client.get(
            f"/company/register_productive_consumption?plan_id={plan}"
        )
        assert '<form method="post"' in response.text
        assert '<form method="get"' not in response.text

    def test_that_plan_info_is_present_in_response_html_if_valid_plan_id_is_given_via_url(
        self,
    ) -> None:
        EXPECTED_PLAN_NAME = "Plan name 1234"
        EXPECTED_PLAN_DESCRIPTION = "Plan description 1234"
        plan = self.plan_generator.create_plan(
            product_name=EXPECTED_PLAN_NAME, description=EXPECTED_PLAN_DESCRIPTION
        )
        response = self.client.get(
            f"/company/register_productive_consumption?plan_id={plan}"
        )
        assert str(plan) in response.text
        assert EXPECTED_PLAN_NAME in response.text
        assert EXPECTED_PLAN_DESCRIPTION in response.text

    def test_that_plan_info_is_present_in_response_html_if_valid_plan_id_is_given_via_form(
        self,
    ) -> None:
        EXPECTED_PLAN_NAME = "Plan name 1234"
        EXPECTED_PLAN_DESCRIPTION = "Plan description 1234"
        plan = self.plan_generator.create_plan(
            product_name=EXPECTED_PLAN_NAME, description=EXPECTED_PLAN_DESCRIPTION
        )
        response = self.client.get(
            "/company/register_productive_consumption",
            data=dict(plan_id=plan, amount=3, type_of_consumption="fixed"),
        )
        assert str(plan) in response.text
        assert EXPECTED_PLAN_NAME in response.text
        assert EXPECTED_PLAN_DESCRIPTION in response.text

    def test_that_amount_from_query_string_appears_in_response_html(self) -> None:
        EXPECTED_AMOUNT = 3
        response = self.client.get(
            f"/company/register_productive_consumption?amount={EXPECTED_AMOUNT}"
        )
        assert str(EXPECTED_AMOUNT) in response.text


class CompanyPostTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_that_logged_in_company_receives_400_when_posting_non_existing_plan_id(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id=str(uuid4()), amount=3, type_of_consumption="fixed"),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_invalid_type_of_consumption(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="unknown"
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_incomplete_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id=self.create_plan(), amount=3),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_gets_redirected_when_posting_valid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="fixed"
            ),
        )
        self.assertEqual(response.status_code, 302)

    def create_plan(self) -> str:
        return str(self.plan_generator.create_plan())
