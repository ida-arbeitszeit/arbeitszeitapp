from arbeitszeit.use_cases.query_plans import PlanFilter, PlanSorting
from arbeitszeit_web.api_controllers.query_plans_api_controller import (
    QueryPlansApiController,
)

from ..base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryPlansApiController)

    def test_that_by_default_a_request_gets_returned_which_sorts_by_activation(self):
        use_case_request = self.controller.get_request()
        self.assertEqual(use_case_request.sorting_category, PlanSorting.by_activation)

    def test_that_by_default_a_request_gets_returned_which_filters_by_plan_id(self):
        use_case_request = self.controller.get_request()
        self.assertEqual(use_case_request.filter_category, PlanFilter.by_plan_id)

    def test_that_by_default_a_request_gets_returned_without_query_string(self):
        use_case_request = self.controller.get_request()
        self.assertIsNone(use_case_request.query_string)
