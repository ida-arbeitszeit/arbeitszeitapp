from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_details import PlanDetails, PlanDetailsService
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.dependency_injection import get_dependency_injector


class PlanDetailsServiceTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.service = self.injector.get(PlanDetailsService)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.planner = self.company_generator.create_company_entity()
        self.plan = self.plan_generator.create_plan(planner=self.planner.id)
        assert self.planner
        details = self.service.get_details_from_plan(self.plan.id)
        assert details is not None
        self.details: PlanDetails = details
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_no_details_is_returned_when_plan_id_does_not_exist(self) -> None:
        details = self.service.get_details_from_plan(uuid4())
        assert not details

    def test_that_correct_planner_id_is_shown(self) -> None:
        self.assertEqual(self.details.plan_id, self.plan.id)

    def test_that_correct_planner_name_is_shown(self) -> None:
        self.assertEqual(self.details.planner_name, self.planner.name)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self) -> None:
        plan = self.plan_generator.create_plan()
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertTrue(details.is_active)

    def test_that_correct_production_costs_are_shown(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.means_cost, Decimal(1))
        self.assertEqual(details.labour_cost, Decimal(2))
        self.assertEqual(details.resources_cost, Decimal(3))

    def test_that_correct_price_per_unit_of_zero_is_shown_when_plan_is_public_service(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.price_per_unit, Decimal(0))

    def test_that_correct_price_per_unit_is_shown_when_plan_is_productive(self) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=False,
            amount=2,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.price_per_unit, Decimal(3))

    def test_that_correct_product_name_is_shown(self) -> None:
        self.assertEqual(self.details.product_name, self.plan.prd_name)

    def test_that_correct_product_description_is_shown(self) -> None:
        self.assertEqual(self.details.description, self.plan.description)

    def test_that_correct_product_unit_is_shown(self) -> None:
        self.assertEqual(self.details.production_unit, self.plan.prd_unit)

    def test_that_correct_amount_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(amount=123)
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.amount, 123)

    def test_that_correct_public_service_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertTrue(details.is_public_service)

    def test_that_correct_availability_is_shown(self) -> None:
        plan = self.plan_generator.create_plan()
        assert plan.is_available
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertTrue(details.is_available)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self) -> None:
        plan = self.plan_generator.create_plan(cooperation=None)
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertFalse(details.is_cooperating)
        self.assertIsNone(details.cooperation)

    def test_that_correct_cooperation_is_shown(self) -> None:
        coop = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(cooperation=coop)
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertTrue(details.is_cooperating)
        self.assertEqual(details.cooperation, coop.id)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.active_days, 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.active_days, 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan()
        self.datetime_service.freeze_time(datetime(2000, 1, 2, hour=1))
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.active_days, 1)

    def test_that_a_plans_timeframe_is_shown_as_active_days_if_plan_is_expired(
        self,
    ) -> None:
        timeframe = 7
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(
            timeframe=timeframe,
        )
        self.datetime_service.freeze_time(datetime(2000, 1, 11))
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertEqual(details.active_days, timeframe)

    def test_that_creation_date_is_shown(self) -> None:
        self.assertEqual(self.details.creation_date, self.plan.plan_creation_date)

    def test_that_approval_date_is_shown_if_it_exists(self) -> None:
        assert self.plan.approval_date
        self.assertEqual(self.details.approval_date, self.plan.approval_date)

    def test_that_expiration_date_is_shown_if_it_exists(self) -> None:
        plan = self.plan_generator.create_plan(timeframe=5)
        assert plan.expiration_date
        details = self.service.get_details_from_plan(plan.id)
        assert details
        self.assertTrue(details.expiration_date)
