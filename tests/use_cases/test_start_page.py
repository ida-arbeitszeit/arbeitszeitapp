from datetime import datetime
from unittest import TestCase

from arbeitszeit.use_cases.start_page import StartPageUseCase
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class UseCaseTester(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(StartPageUseCase)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_empty_list_is_returned_if_no_plans_exist(self) -> None:
        response = self.use_case.show_start_page()
        self.assertFalse(response.latest_plans)

    def test_that_empty_list_is_returned_if_a_draft_exists(self) -> None:
        self.plan_generator.draft_plan()
        response = self.use_case.show_start_page()
        self.assertFalse(response.latest_plans)

    def test_that_three_plans_are_returned_if_four_plans_exists(self) -> None:
        for _ in range(4):
            self.plan_generator.create_plan()
        response = self.use_case.show_start_page()
        self.assertEqual(len(response.latest_plans), 3)

    def test_that_correct_activation_date_of_plan_is_returned(self) -> None:
        expected_date = datetime(2022, 12, 1, 10)
        self.datetime_service.freeze_time(expected_date)
        self.plan_generator.create_plan()
        response = self.use_case.show_start_page()
        self.assertEqual(response.latest_plans[0].activation_date, expected_date)

    def test_that_correct_plan_id_is_returned(self) -> None:
        expected_plan_id = self.plan_generator.create_plan()
        response = self.use_case.show_start_page()
        self.assertEqual(response.latest_plans[0].plan_id, expected_plan_id)

    def test_that_correct_product_name_of_plan_is_returned(self) -> None:
        expected_product_name = "test product name 123"
        self.plan_generator.create_plan(product_name=expected_product_name)
        response = self.use_case.show_start_page()
        self.assertEqual(response.latest_plans[0].product_name, expected_product_name)
