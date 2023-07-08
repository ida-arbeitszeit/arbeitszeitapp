from datetime import datetime
from unittest import TestCase

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases.calculate_fic_and_update_expired_plans import (
    CalculateFicAndUpdateExpiredPlans,
)
from arbeitszeit.use_cases.hide_plan import HidePlan
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.hide_plan = self.injector.get(HidePlan)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.now = datetime(2000, 1, 1)
        self.calculate_fic_and_update_expired_plans = self.injector.get(
            CalculateFicAndUpdateExpiredPlans
        )
        self.datetime_service.freeze_time(self.now)

    def test_that_correct_plan_gets_hidden_attribute_set_to_true(self):
        plan1 = self.create_expired_plan()
        plan2 = self.create_expired_plan()
        plan3 = self.create_expired_plan()
        self.hide_plan(plan2.id)
        self.assertFalse(plan1.hidden_by_user)
        self.assertTrue(plan2.hidden_by_user)
        self.assertFalse(plan3.hidden_by_user)

    def test_that_correct_response_gets_returned(self):
        plan = self.create_expired_plan()
        response = self.hide_plan(plan.id)
        self.assertEqual(response.plan_id, plan.id)
        self.assertEqual(response.is_success, True)

    def test_that_active_plans_do_not_get_hidden_and_correct_response_gets_returned(
        self,
    ):
        plan = self.create_active_plan()
        response = self.hide_plan(plan.id)
        assert response.plan_id == plan.id
        assert response.is_success == False

    def create_expired_plan(self) -> Plan:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.unfreeze_time()
        self.calculate_fic_and_update_expired_plans()
        return plan

    def create_active_plan(self) -> Plan:
        return self.plan_generator.create_plan()
