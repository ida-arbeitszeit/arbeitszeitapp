from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.plan_details import PlanDetails, PlanDetailsService
from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.dependency_injection import get_dependency_injector


class PlanDetailsServiceTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.service = self.injector.get(PlanDetailsService)
        self.approve_plan_use_case = self.injector.get(ApprovePlanUseCase)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.planner = self.company_generator.create_company_record()
        self.plan = self.plan_generator.create_plan(planner=self.planner.id)
        assert self.planner
        details = self.service.get_details_from_plan(self.plan)
        assert details is not None
        self.details: PlanDetails = details
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_no_details_is_returned_when_plan_id_does_not_exist(self) -> None:
        details = self.service.get_details_from_plan(uuid4())
        assert not details

    def test_that_correct_planner_id_is_shown(self) -> None:
        self.assertEqual(self.details.plan_id, self.plan)

    def test_that_correct_planner_name_is_shown(self) -> None:
        self.assertEqual(self.details.planner_name, self.planner.name)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self) -> None:
        plan = self.plan_generator.create_plan()
        details = self.service.get_details_from_plan(plan)
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
        details = self.service.get_details_from_plan(plan)
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
        details = self.service.get_details_from_plan(plan)
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
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.price_per_unit, Decimal(3))

    @parameterized.expand(
        [
            ("test product name",),
            ("another product name",),
        ]
    )
    def test_that_correct_product_name_is_shown(
        self, expected_product_name: str
    ) -> None:
        plan = self.plan_generator.create_plan(product_name=expected_product_name)
        details = self.service.get_details_from_plan(plan)
        assert details
        assert details.product_name == expected_product_name

    @parameterized.expand(
        [
            ("test description",),
            ("another description",),
        ]
    )
    def test_that_correct_product_description_is_shown(
        self, expected_description: str
    ) -> None:
        plan = self.plan_generator.create_plan(description=expected_description)
        details = self.service.get_details_from_plan(plan)
        assert details
        assert details.description == expected_description

    @parameterized.expand(
        [
            ("test unit",),
            ("another test unit",),
        ]
    )
    def test_that_correct_product_unit_is_shown(self, expected_unit: str) -> None:
        plan = self.plan_generator.create_plan(production_unit=expected_unit)
        details = self.service.get_details_from_plan(plan)
        assert details
        assert details.production_unit == expected_unit

    def test_that_correct_amount_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(amount=123)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.amount, 123)

    def test_that_correct_public_service_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertTrue(details.is_public_service)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self) -> None:
        plan = self.plan_generator.create_plan(cooperation=None)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertFalse(details.is_cooperating)
        self.assertIsNone(details.cooperation)

    def test_that_correct_cooperation_is_shown(self) -> None:
        coop = self.coop_generator.create_cooperation()
        plan = self.plan_generator.create_plan(cooperation=coop)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertTrue(details.is_cooperating)
        self.assertEqual(details.cooperation, coop)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.active_days, 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.active_days, 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan()
        self.datetime_service.freeze_time(datetime(2000, 1, 2, hour=1))
        details = self.service.get_details_from_plan(plan)
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
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.active_days, timeframe)

    @parameterized.expand(
        [
            (datetime(2000, 1, 1), timedelta(days=1)),
            (datetime(2001, 2, 2), timedelta(hours=1)),
        ]
    )
    def test_that_creation_date_is_shown(
        self, expected_creation_date: datetime, time_since_creation: timedelta
    ) -> None:
        self.datetime_service.freeze_time(expected_creation_date)
        plan = self.plan_generator.create_plan()
        self.datetime_service.advance_time(time_since_creation)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.creation_date, expected_creation_date)

    @parameterized.expand(
        [
            (datetime(2000, 1, 1), timedelta(days=1), timedelta(days=1)),
            (datetime(2001, 2, 2), timedelta(hours=1), timedelta(days=2)),
        ]
    )
    def test_that_approval_date_is_shown_if_it_exists(
        self,
        expected_approval_date: datetime,
        time_between_creation_and_approval: timedelta,
        time_since_approval: timedelta,
    ) -> None:
        self.datetime_service.freeze_time(
            expected_approval_date - time_between_creation_and_approval
        )
        plan = self.plan_generator.create_plan(approved=False)
        self.datetime_service.freeze_time(expected_approval_date)
        self.approve_plan(plan)
        self.datetime_service.advance_time(time_since_approval)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertEqual(details.approval_date, expected_approval_date)

    def test_that_expiration_date_is_shown_if_it_exists(self) -> None:
        plan = self.plan_generator.create_plan(timeframe=5)
        details = self.service.get_details_from_plan(plan)
        assert details
        self.assertTrue(details.expiration_date)

    def approve_plan(self, plan: UUID) -> None:
        request = ApprovePlanUseCase.Request(plan=plan)
        response = self.approve_plan_use_case.approve_plan(request)
        assert response.is_approved
