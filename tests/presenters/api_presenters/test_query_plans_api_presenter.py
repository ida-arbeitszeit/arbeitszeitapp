import json
from typing import Any

from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from tests.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedPlanGenerator


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryPlansApiPresenter)
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)

    def test_that_json_string_has_empty_results_if_no_plans_exist(self):
        use_case_response = self.queried_plan_generator.get_response(queried_plans=[])
        json_string = self.presenter.get_json(use_case_response)
        deserialized = self.deserialize(json_string)
        self.assertFalse(deserialized["results"])

    def test_that_json_string_has_one_result_if_one_plan_exists(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[self.queried_plan_generator.get_plan()]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = self.deserialize(json_string)
        self.assertEqual(len(deserialized["results"]), 1)

    def test_that_json_string_has_two_results_if_two_plans_exist(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[
                self.queried_plan_generator.get_plan(),
                self.queried_plan_generator.get_plan(),
            ]
        )
        json_string = self.presenter.get_json(use_case_response)
        deserialized = self.deserialize(json_string)
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
        deserialized = self.deserialize(json_string)
        queried_plan = deserialized["results"][0]
        for key in expected_keys:
            self.assertIn(key, queried_plan)

    def deserialize(self, json_string: str) -> Any:
        return json.loads(json_string)
