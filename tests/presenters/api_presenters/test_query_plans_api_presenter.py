import json
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from tests.data_generators import QueriedPlanGenerator

from ..base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryPlansApiPresenter)
        self.queried_plan_generator = QueriedPlanGenerator()

    def test_that_json_string_has_empty_results_if_no_plans_exist(self):
        use_case_response = self.queried_plan_generator.get_response(queried_plans=[])
        json_string = self.presenter.get_json(use_case_response)
        self.assertEqual(json_string, '{"results": []}')

    def test_that_json_string_has_one_result_if_one_plan_exists(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[self.queried_plan_generator.get_plan()]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        self.assertEqual(len(deserialized["results"]), 1)

    def test_that_json_string_has_two_results_if_two_plans_exist(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(),
                self.queried_plan_generator.get_plan(),
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        self.assertEqual(len(deserialized["results"]), 2)

    def test_expected_keys_in_json_string(self):
        expected_keys = [
            "plan_id",
            "company_name",
            "company_id",
            "product_name",
            "description",
            "price_per_unit",
            "is_public_service",
            "is_available",
            "is_cooperating",
            "activation_date",
        ]
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[self.queried_plan_generator.get_plan()]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        queried_plan = deserialized["results"][0]
        for key in expected_keys:
            self.assertIn(key, queried_plan)

    def test_json_has_correct_activation_date_in_iso_8601_format_when_no_microseconds_are_given(
        self,
    ):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(
                    activation_date=datetime(
                        year=2022, month=5, day=1, hour=15, minute=30, second=10
                    )
                )
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        queried_plan = deserialized["results"][0]
        self.assertEqual(queried_plan["activation_date"], "2022-05-01T15:30:10")

    def test_json_has_correct_activation_date_in_iso_8601_format_when_microseconds_are_given(
        self,
    ):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(
                    activation_date=datetime(
                        year=2022,
                        month=5,
                        day=1,
                        hour=15,
                        minute=30,
                        second=10,
                        microsecond=2222,
                    )
                )
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        queried_plan = deserialized["results"][0]
        self.assertEqual(queried_plan["activation_date"], "2022-05-01T15:30:10.002222")

    def test_json_shows_correct_decimal_number_for_price_per_unit(
        self,
    ):
        expected_price = Decimal("5.001")
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(price_per_unit=expected_price)
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        queried_plan = deserialized["results"][0]
        self.assertEqual(queried_plan["price_per_unit"], "5.001")

    def test_json_shows_correct_company_id(
        self,
    ):
        expected_company_id = uuid4()
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(company_id=expected_company_id)
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = json.loads(json_string)
        queried_plan = deserialized["results"][0]
        self.assertEqual(queried_plan["company_id"], str(expected_company_id))
