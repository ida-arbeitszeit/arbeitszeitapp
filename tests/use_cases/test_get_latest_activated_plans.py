from datetime import datetime
from unittest import TestCase

from arbeitszeit.use_cases.get_latest_activated_plans import GetLatestActivatedPlans
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class UseCaseTest(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(GetLatestActivatedPlans)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = FakeDatetimeService()

    def test_returns_nothing_when_there_are_no_plans(self):
        response = self.use_case()
        self.assertFalse(response.plans)

    def test_returns_nothing_when_there_is_only_one_inactive_plan(self):
        self.plan_generator.create_plan()
        response = self.use_case()
        self.assertFalse(response.plans)

    def test_returns_correct_plan_id_of_active_plan(self):
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        response = self.use_case()
        self.assertEqual(response.plans[0].plan_id, plan.id)

    def test_returns_correct_prd_name_of_active_plan(self):
        expected_name = "prd test name"
        self.plan_generator.create_plan(
            activation_date=datetime.min, product_name=expected_name
        )
        response = self.use_case()
        self.assertEqual(response.plans[0].prd_name, expected_name)

    def test_returns_correct_activation_date_of_active_plan(self):
        expected_activation_date = datetime(2022, 5, 16, 20, 50)

        self.plan_generator.create_plan(activation_date=expected_activation_date)
        response = self.use_case()
        self.assertEqual(response.plans[0].activation_date, expected_activation_date)

    def test_returns_always_three_active_plans(self):
        for i in range(5):
            self.plan_generator.create_plan(activation_date=datetime.min)
        response = self.use_case()
        self.assertEqual(response.plans.__len__(), 3)

    def test_returns_three_active_plans_in_correct_order(self):
        timestamps = [
            None,
            self.datetime_service.now_minus_two_days(),
            self.datetime_service.now_minus_one_day(),  # second latest
            self.datetime_service.now_minus_ten_days(),
            self.datetime_service.now_minus_20_hours(),  # latest
            self.datetime_service.now_minus_25_hours(),  # third latest
        ]
        unordered_plans = [
            self.plan_generator.create_plan(activation_date=t) for t in timestamps
        ]
        response = self.use_case()
        self.assertEqual(response.plans[0].plan_id, unordered_plans[4].id)
        self.assertEqual(response.plans[1].plan_id, unordered_plans[2].id)
        self.assertEqual(response.plans[2].plan_id, unordered_plans[5].id)
