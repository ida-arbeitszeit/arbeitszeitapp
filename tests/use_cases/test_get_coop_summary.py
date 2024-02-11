from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Optional
from uuid import uuid4

from pytest import approx

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.get_coop_summary import (
    GetCoopSummary,
    GetCoopSummaryRequest,
    GetCoopSummaryResponse,
)

from .base_test_case import BaseTestCase


class GetCoopSummaryTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_coop_summary = self.injector.get(GetCoopSummary)

    def test_that_none_is_returned_when_cooperation_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_record()
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, uuid4()))
        assert summary is None

    def test_that_requester_is_correctly_defined_as_equal_to_coordinator(self) -> None:
        requester = self.company_generator.create_company_record()
        coop = self.cooperation_generator.create_cooperation(coordinator=requester)
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(summary, lambda s: s.requester_is_coordinator == True)

    def test_that_requester_is_correctly_defined_as_different_from_coordinator(
        self,
    ) -> None:
        requester = self.company_generator.create_company_record()
        coop = self.cooperation_generator.create_cooperation()
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(summary, lambda s: s.requester_is_coordinator == False)

    def test_that_correct_amount_of_associated_plans_are_shown(self) -> None:
        requester = self.company_generator.create_company_record()
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(plans=[plan1, plan2])
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(summary, lambda s: len(s.plans) == 2)

    def test_that_correct_coordinator_id_is_shown(self) -> None:
        requester = self.company_generator.create_company_record()
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(
            plans=[plan1, plan2], coordinator=requester.id
        )
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(summary, lambda s: s.current_coordinator == requester.id)

    def test_that_correct_coordinator_id_is_shown_when_several_cooperations_exist(
        self,
    ) -> None:
        requester = self.company_generator.create_company_record()
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()

        self.cooperation_generator.create_cooperation()
        coop = self.cooperation_generator.create_cooperation(
            plans=[plan1, plan2], coordinator=requester.id
        )
        self.cooperation_generator.create_cooperation()

        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(summary, lambda s: s.current_coordinator == requester.id)

    def test_that_correct_coordinator_name_is_shown(self) -> None:
        expected_coordinator_name = "expected coordinator name"
        coordinator = self.company_generator.create_company(
            name=expected_coordinator_name
        )
        requester = self.company_generator.create_company_record()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester.id, coop))
        self.assert_success(
            summary, lambda s: s.current_coordinator_name == expected_coordinator_name
        )

    def test_that_inactive_plans_do_not_show_up_in_cooperation_summary(self) -> None:
        requester = self.company_generator.create_company()
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan = self.plan_generator.create_plan(timeframe=1)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        self.datetime_service.advance_time(timedelta(days=2))
        summary = self.get_coop_summary(GetCoopSummaryRequest(requester, coop))
        self.assert_success(summary, lambda s: len(s.plans) == 0)

    def test_that_coop_price_is_none_if_there_are_no_plans_associated(self) -> None:
        coop = self.cooperation_generator.create_cooperation(plans=None)
        summary = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        self.assert_success(summary, lambda s: s.coop_price is None)

    def test_that_coop_price_equals_individual_price_when_there_is_one_plan_in_a_cooperation(
        self,
    ) -> None:
        expected_price = approx(Decimal(2))
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
        )
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        summary = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        self.assert_success(summary, lambda s: s.coop_price == expected_price)

    def test_that_correct_coop_price_is_calculated_when_there_are_two_plans_in_a_cooperation(
        self,
    ) -> None:
        expected_price = approx(Decimal("0.75"))
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(1)),
            amount=10,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(4), Decimal(4), Decimal(2)),
            amount=10,
        )
        coop = self.cooperation_generator.create_cooperation(plans=[plan1, plan2])
        summary = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        self.assert_success(summary, lambda s: s.coop_price == expected_price)

    def assert_success(
        self,
        response: Optional[GetCoopSummaryResponse],
        assertion: Callable[[GetCoopSummaryResponse], bool],
    ) -> None:
        assert response
        assert assertion(response)


class AssociatedPlansTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_coop_summary = self.injector.get(GetCoopSummary)

    def test_that_summary_of_a_cooperation_with_two_plans_shows_two_associated_plans(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(plans=[plan1, plan2])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert len(response.plans) == 2

    def test_that_associated_plan_in_a_summary_has_correct_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].plan_id == plan

    def test_that_associated_plan_in_a_summary_has_correct_plan_name(self) -> None:
        expected_prd_name = "A product name"
        plan = self.plan_generator.create_plan(product_name=expected_prd_name)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].plan_name == expected_prd_name

    def test_that_associated_plan_in_a_summary_has_correct_individual_price(
        self,
    ) -> None:
        expected_price = Decimal("0.5")
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(1)),
            amount=10,
        )
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].plan_individual_price == expected_price

    def test_that_associated_plan_in_a_summary_has_correct_individual_price_when_there_is_a_second_plan(
        self,
    ) -> None:
        expected_price = Decimal("0.5")
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(1)),
            amount=10,
        )
        self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(4), Decimal(4), Decimal(2)),
            amount=10,
        )
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].plan_individual_price == expected_price

    def test_that_associated_plan_in_a_summary_has_correct_planner_id(self) -> None:
        expected_planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=expected_planner)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].planner_id == expected_planner

    def test_that_associated_plan_in_a_summary_has_correct_planner_name(self) -> None:
        expected_planner_name = "The Cooperating Coop"
        planner = self.company_generator.create_company(name=expected_planner_name)
        plan = self.plan_generator.create_plan(planner=planner)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(GetCoopSummaryRequest(uuid4(), coop))
        assert response
        assert response.plans[0].planner_name == expected_planner_name

    def test_that_associated_plan_shows_that_planner_is_also_requester_of_coop_summary(
        self,
    ) -> None:
        expected_planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=expected_planner)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(
            GetCoopSummaryRequest(requester_id=expected_planner, coop_id=coop)
        )
        assert response
        assert response.plans[0].requester_is_planner == True

    def test_that_associated_plan_shows_that_planner_is_not_requester_of_coop_summary(
        self,
    ) -> None:
        expected_planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=expected_planner)
        coop = self.cooperation_generator.create_cooperation(plans=[plan])
        response = self.get_coop_summary(
            GetCoopSummaryRequest(requester_id=uuid4(), coop_id=coop)
        )
        assert response
        assert response.plans[0].requester_is_planner == False
