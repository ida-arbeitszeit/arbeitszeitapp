from decimal import Decimal
from typing import Dict

from parameterized import parameterized

from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase

from .flask import ViewTestCase


class AuthenticatedCompanyTestsForGet(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_get_200_without_url_parameter(
        self,
    ) -> None:
        url = "/company/create_draft"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_200_with_existing_expired_plan_as_url_parameter(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/company/create_draft?expired_plan_id={str(plan)}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTestsForPost(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.show_my_plans = self.injector.get(ShowMyPlansUseCase)

    def test_post_user_saving_draft_leads_to_302_and_draft_gets_created(self) -> None:
        self.assertFalse(self._count_drafts_of_company())
        test_data = self._create_form_data()
        response = self.client.post("/company/create_draft", data=test_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self._count_drafts_of_company(),
            1,
        )

    def test_posting_invalid_form_data_yields_status_code_400(self) -> None:
        response = self.client.post("/company/create_draft", data={})
        assert response.status_code == 400

    @parameterized.expand(
        [
            ("testname 123",),
            ("other test name",),
        ]
    )
    def test_posting_invalid_form_data_yields_response_that_contains_the_original_form_field_values(
        self, expected_product_name
    ) -> None:
        response = self.client.post(
            "/company/create_draft", data=dict(prd_name=expected_product_name)
        )
        assert expected_product_name in response.text

    def _create_form_data(self) -> Dict:
        return dict(
            prd_name="test name",
            description="test description",
            timeframe=14,
            prd_unit="1 piece",
            prd_amount=10,
            costs_p=Decimal("10.5"),
            costs_r=Decimal("15"),
            costs_a=Decimal("20"),
            productive_or_public=True,
        )

    def _count_drafts_of_company(self) -> int:
        request = ShowMyPlansRequest(company_id=self.company.id)
        response = self.show_my_plans.show_company_plans(request)
        return len(response.drafts)
