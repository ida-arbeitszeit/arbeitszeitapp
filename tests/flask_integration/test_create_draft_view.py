from decimal import Decimal
from typing import Dict

from parameterized import parameterized

from arbeitszeit.interactors.show_my_plans import (
    ShowMyPlansInteractor,
    ShowMyPlansRequest,
)

from .flask import ViewTestCase


class AuthenticatedCompanyTestsForGet(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_get_request_of_logged_in_company_leads_to_200(
        self,
    ) -> None:
        url = "/company/create_draft"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTestsForPost(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.show_my_plans = self.injector.get(ShowMyPlansInteractor)

    def test_post_user_saving_draft_leads_to_302_and_draft_gets_created(self) -> None:
        self.assertFalse(self._count_drafts_of_company())
        test_data = self._create_form_data()
        response = self.client.post("/company/create_draft", data=test_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self._count_drafts_of_company(),
            1,
        )

    def test_posting_invalid_form_data_leads_to_display_of_error_messages(self) -> None:
        GENERAL_ERROR_MESSAGE = "Please correct the errors in the form."
        MISSING_FIELD_ERROR_MESSAGE = "This field is required."
        response = self.client.post("/company/create_draft", data={})
        assert response.status_code == 400
        assert GENERAL_ERROR_MESSAGE in response.text
        assert MISSING_FIELD_ERROR_MESSAGE in response.text

    @parameterized.expand(
        [
            ("testname 123",),
            ("  other test name  ",),
        ]
    )
    def test_posting_invalid_form_data_yields_response_that_contains_the_original_form_field_values(
        self, expected_product_name: str
    ) -> None:
        response = self.client.post(
            "/company/create_draft", data=dict(prd_name=expected_product_name)
        )
        assert response.status_code == 400
        assert expected_product_name in response.text

    def test_posting_only_zero_costs_leads_to_correct_error_message(self) -> None:
        response = self.client.post(
            "/company/create_draft",
            data=self._create_form_data(
                costs_p=Decimal("0"), costs_r=Decimal("0"), costs_a=Decimal("0")
            ),
        )
        assert response.status_code == 400
        assert (
            "At least one of the costs fields must be a positive number of hours."
            in response.text
        )

    def _create_form_data(
        self,
        costs_p: Decimal | None = Decimal("10.5"),
        costs_r: Decimal | None = Decimal("15"),
        costs_a: Decimal | None = Decimal("20"),
    ) -> Dict:
        return dict(
            prd_name="test name",
            description="test description",
            timeframe=14,
            prd_unit="1 piece",
            prd_amount=10,
            costs_p=costs_p,
            costs_r=costs_r,
            costs_a=costs_a,
            productive_or_public=True,
        )

    def _count_drafts_of_company(self) -> int:
        request = ShowMyPlansRequest(company_id=self.company)
        response = self.show_my_plans.show_company_plans(request)
        return len(response.drafts)
