from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Union
from uuid import uuid4

from arbeitszeit.entities import Plan, ProductionCosts
from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from arbeitszeit_flask.database.repositories import PlanRepository
from tests.datetime_service import FakeDatetimeService

from ..data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from .flask import FlaskTestCase

Number = Union[int, Decimal]


def production_costs(a: Number, r: Number, p: Number) -> ProductionCosts:
    return ProductionCosts(
        Decimal(a),
        Decimal(r),
        Decimal(p),
    )


class PlanRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_plan_gets_hidden(self) -> None:
        plan = self.plan_generator.create_plan()
        self.plan_repository.hide_plan(plan.id)
        plan_from_repo = self.plan_repository.get_plans().with_id(plan.id).first()
        assert plan_from_repo
        assert plan_from_repo.hidden_by_user

    def test_that_availability_is_toggled_to_false(self) -> None:
        plan = self.plan_generator.create_plan()
        assert plan.is_available == True
        self.plan_repository.toggle_product_availability(plan)
        plan_from_repo = self.plan_repository.get_plans().with_id(plan.id).first()
        assert plan_from_repo
        assert plan_from_repo.is_available == False

    def test_that_availability_is_toggled_to_true(self) -> None:
        plan = self.plan_generator.create_plan(is_available=False)
        assert plan.is_available == False
        self.plan_repository.toggle_product_availability(plan)
        plan_from_repo = self.plan_repository.get_plans().with_id(plan.id).first()
        assert plan_from_repo
        assert plan_from_repo.is_available == True

    def test_create_plan_propagates_specified_arguments_to_created_plan(self) -> None:
        expected_planner = self.company_generator.create_company()
        plan = self.plan_repository.create_plan(
            creation_timestamp=(expected_timestamp := datetime(2000, 1, 1)),
            planner=expected_planner,
            production_costs=(
                expected_costs := ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
            ),
            product_name=(expected_product_name := "test product name"),
            distribution_unit=(expected_distribution_unit := "test unit"),
            amount_produced=(expected_amount := 642),
            product_description=(expected_description := "test description"),
            duration_in_days=(expected_duration := 631),
            is_public_service=(expected_is_public_service := False),
        )
        assert plan.plan_creation_date == expected_timestamp
        assert plan.planner == expected_planner
        assert plan.production_costs == expected_costs
        assert plan.prd_name == expected_product_name
        assert plan.prd_unit == expected_distribution_unit
        assert plan.prd_amount == expected_amount
        assert plan.description == expected_description
        assert plan.timeframe == expected_duration
        assert plan.is_public_service == expected_is_public_service

    def test_that_created_plan_can_have_its_approval_date_changed(self) -> None:
        plan = self.create_plan()
        expected_approval_date = datetime(2000, 3, 2)
        self.plan_repository.get_plans().with_id(plan.id).update().set_approval_date(
            expected_approval_date
        ).perform()
        changed_plan: Plan = self.plan_repository.get_plans().with_id(plan.id).first()  # type: ignore
        assert changed_plan.approval_date == expected_approval_date

    def create_plan(self) -> Plan:
        return self.plan_repository.create_plan(
            creation_timestamp=datetime(2000, 1, 1),
            planner=self.company_generator.create_company(),
            production_costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            product_name="test product name",
            distribution_unit="test unit",
            amount_produced=642,
            product_description="test description",
            duration_in_days=631,
            is_public_service=False,
        )


class GetActivePlansTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.approve_plan_use_case = self.injector.get(ApprovePlanUseCase)

    def test_plans_can_be_ordered_by_creation_date_in_descending_order(
        self,
    ) -> None:
        creation_dates = [
            self.datetime_service.now_minus_ten_days(),
            self.datetime_service.now(),
            self.datetime_service.now_minus_20_hours(),
            self.datetime_service.now_minus_25_hours(),
            self.datetime_service.now_minus_one_day(),
        ]
        plans: List[Plan] = list()
        for timestamp in creation_dates:
            self.datetime_service.freeze_time(timestamp)
            plans.append(self.plan_generator.create_plan())
        self.datetime_service.unfreeze_time()
        retrieved_plans = list(
            self.plan_repository.get_plans()
            .ordered_by_creation_date(ascending=False)
            .limit(3)
        )
        assert len(retrieved_plans) == 3
        assert retrieved_plans[0] == plans[1]
        assert retrieved_plans[1] == plans[2]
        assert retrieved_plans[2] == plans[4]

    def test_plans_can_be_ordered_by_activation_date_in_descending_order(
        self,
    ) -> None:
        activation_dates = [
            self.datetime_service.now_minus_ten_days(),
            self.datetime_service.now(),
            self.datetime_service.now_minus_20_hours(),
            self.datetime_service.now_minus_25_hours(),
            self.datetime_service.now_minus_one_day(),
        ]
        plans: List[Plan] = list()
        for timestamp in activation_dates:
            self.datetime_service.freeze_time(timestamp)
            plans.append(self.plan_generator.create_plan())
        self.datetime_service.unfreeze_time()
        retrieved_plans = list(
            self.plan_repository.get_plans()
            .ordered_by_activation_date(ascending=False)
            .limit(3)
        )
        assert len(retrieved_plans) == 3
        assert retrieved_plans[0] == plans[1]
        assert retrieved_plans[1] == plans[2]
        assert retrieved_plans[2] == plans[4]

    def test_plans_can_be_ordered_by_planner_name(
        self,
    ) -> None:
        planner_names = ["1_name", "B_name", "d_name", "c_name"]
        planners = [
            self.company_generator.create_company_entity(name=name)
            for name in planner_names
        ]
        plans: List[Plan] = list()
        for company in planners:
            plans.append(self.plan_generator.create_plan(planner=company.id))
        retrieved_plans = list(
            self.plan_repository.get_plans().ordered_by_planner_name().limit(3)
        )
        assert len(retrieved_plans) == 3
        assert retrieved_plans[0] == plans[0]
        assert retrieved_plans[1] == plans[1]
        assert retrieved_plans[2] == plans[3]

    def test_that_plans_can_be_filtered_by_product_name(self) -> None:
        expected_plan = self.plan_generator.create_plan(
            product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.get_plans().with_product_name_containing(
                "Delivery of goods"
            )
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_plans_can_be_filtered_by_substrings_of_product_name(
        self,
    ) -> None:
        expected_plan = self.plan_generator.create_plan(
            product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.get_plans().with_product_name_containing("very of go")
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_query_plans_by_substring_of_plan_id_returns_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        expected_plan_id = expected_plan.id
        query = str(expected_plan_id)[3:8]
        returned_plan = list(self.plan_repository.get_plans().with_id_containing(query))
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_plans_that_ordering_by_creation_date_works_even_when_plan_activation_was_in_reverse_order(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_plan = self.plan_generator.create_plan(approved=False)
        self.datetime_service.freeze_time(datetime(2000, 1, 2))
        second_plan = self.plan_generator.create_plan(approved=False)
        self.datetime_service.freeze_time(datetime(2000, 1, 3))
        self.approve_plan_use_case.approve_plan(
            request=ApprovePlanUseCase.Request(
                plan=second_plan.id,
            )
        )
        self.datetime_service.freeze_time(datetime(2000, 1, 4))
        self.approve_plan_use_case.approve_plan(
            request=ApprovePlanUseCase.Request(
                plan=first_plan.id,
            )
        )
        plans = list(self.plan_repository.get_plans().ordered_by_creation_date())
        assert plans[0].id == first_plan.id
        assert plans[1].id == second_plan.id


class GetAllPlans(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_that_without_any_plans_nothing_is_returned(self) -> None:
        assert not list(self.plan_repository.get_plans())

    def test_that_unapproved_plans_are_returned(self) -> None:
        self.plan_generator.create_plan(approved=False)
        assert list(self.plan_repository.get_plans())

    def test_that_approved_plans_are_returned(self) -> None:
        self.plan_generator.create_plan(approved=True)
        assert list(self.plan_repository.get_plans())

    def test_that_can_filter_unapproved_plans_from_results(self) -> None:
        self.plan_generator.create_plan(approved=False)
        assert not list(self.plan_repository.get_plans().that_are_approved())

    def test_can_filter_public_plans(self) -> None:
        self.plan_generator.create_plan(is_public_service=False)
        assert not list(self.plan_repository.get_plans().that_are_public())
        self.plan_generator.create_plan(is_public_service=True)
        assert list(self.plan_repository.get_plans().that_are_public())

    def test_can_filter_productive_plans(self) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        assert not list(self.plan_repository.get_plans().that_are_productive())
        self.plan_generator.create_plan(is_public_service=False)
        assert list(self.plan_repository.get_plans().that_are_productive())

    def test_can_count_all_plans(self) -> None:
        self.plan_generator.create_plan()
        assert len(self.plan_repository.get_plans()) == 1
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        assert len(self.plan_repository.get_plans()) == 3

    def test_can_filter_by_planner(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan()
        assert not self.plan_repository.get_plans().planned_by(planner)
        self.plan_generator.create_plan(planner=planner)
        assert self.plan_repository.get_plans().planned_by(planner)

    def test_can_filter_plans_by_multiple_planners(self) -> None:
        planner_1 = self.company_generator.create_company()
        planner_2 = self.company_generator.create_company()
        self.plan_generator.create_plan()
        self.plan_generator.create_plan(planner=planner_1)
        self.plan_generator.create_plan(planner=planner_2)
        assert (
            len(self.plan_repository.get_plans().planned_by(planner_1, planner_2)) == 2
        )

    def test_can_get_plan_by_its_id(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        assert expected_plan in self.plan_repository.get_plans().with_id(
            expected_plan.id
        )

    def test_can_filter_plans_by_multiple_ids(self) -> None:
        expected_plan_1 = self.plan_generator.create_plan()
        expected_plan_2 = self.plan_generator.create_plan()
        other_plan = self.plan_generator.create_plan()
        query = self.plan_repository.get_plans().with_id(
            expected_plan_1.id, expected_plan_2.id
        )
        assert expected_plan_1 in query
        assert expected_plan_2 in query
        assert other_plan not in query

    def test_nothing_is_returned_if_plan_with_specified_uuid_is_not_present(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        assert not self.plan_repository.get_plans().with_id(uuid4())

    def test_can_filter_results_for_unreviewed_plans(self) -> None:
        self.plan_generator.create_plan(approved=True)
        assert not self.plan_repository.get_plans().without_completed_review()

    def test_filtering_unreviewed_plans_will_still_contain_unreviewed_plans(
        self,
    ) -> None:
        self.plan_generator.create_plan(approved=False)
        assert self.plan_repository.get_plans().without_completed_review()

    def test_that_plans_with_open_cooperation_request_can_be_filtered(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        requesting_plan = self.plan_generator.create_plan(requested_cooperation=coop)
        non_requesting_plan = self.plan_generator.create_plan()
        results = self.plan_repository.get_plans().with_open_cooperation_request()
        assert requesting_plan.id in [plan.id for plan in results]
        assert non_requesting_plan.id not in [plan.id for plan in results]

    def test_that_plans_with_open_cooperation_request_at_specific_coop_can_be_filtered(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        other_coop = self.cooperation_generator.create_cooperation()
        plan_requesting_at_coop = self.plan_generator.create_plan(
            requested_cooperation=coop
        )
        plan_requesting_at_other_coop = self.plan_generator.create_plan(
            requested_cooperation=other_coop
        )
        results = self.plan_repository.get_plans().with_open_cooperation_request(
            cooperation=coop.id
        )
        assert plan_requesting_at_coop.id in [plan.id for plan in results]
        assert plan_requesting_at_other_coop.id not in [plan.id for plan in results]

    def test_can_filter_for_cooperating_plans(self):
        coop = self.cooperation_generator.create_cooperation()
        cooperating_plan = self.plan_generator.create_plan(cooperation=coop)
        non_cooperating_plan = self.plan_generator.create_plan(cooperation=None)
        results = self.plan_repository.get_plans().that_are_cooperating()
        assert cooperating_plan.id in [plan.id for plan in results]
        assert non_cooperating_plan.id not in [plan.id for plan in results]

    def test_plan_without_cooperation_is_considered_to_be_only_plan_in_its_own_cooperation(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(cooperation=None)
        cooperating_plans = (
            self.plan_repository.get_plans().that_are_in_same_cooperation_as(plan.id)
        )
        assert len(cooperating_plans) == 1
        assert plan in cooperating_plans

    def test_that_plans_outside_of_cooperation_are_excluded_when_filtering_for_cooperating_plans(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        plan1 = self.plan_generator.create_plan(cooperation=coop)
        plan2 = self.plan_generator.create_plan(cooperation=coop)
        self.plan_generator.create_plan(requested_cooperation=None)
        cooperating_plans = (
            self.plan_repository.get_plans().that_are_in_same_cooperation_as(plan1.id)
        )
        assert len(cooperating_plans) == 2
        assert plan1.id in [p.id for p in cooperating_plans]
        assert plan2.id in [p.id for p in cooperating_plans]

    def test_can_filter_plans_that_are_part_of_any_cooperation(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(cooperation=cooperation)
        plans = self.plan_repository.get_plans().that_are_part_of_cooperation()
        assert plans

    def test_can_filter_plans_from_multiple_cooperations(self) -> None:
        cooperation1 = self.cooperation_generator.create_cooperation()
        cooperation2 = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(cooperation=cooperation1)
        self.plan_generator.create_plan(cooperation=cooperation2)
        plans = self.plan_repository.get_plans().that_are_part_of_cooperation(
            cooperation1.id, cooperation2.id
        )
        assert len(plans) == 2

    def test_correct_plans_in_cooperation_returned(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        plan1 = self.plan_generator.create_plan(cooperation=coop)
        plan2 = self.plan_generator.create_plan(cooperation=coop)
        plan3 = self.plan_generator.create_plan(requested_cooperation=None)
        plans = self.plan_repository.get_plans().that_are_part_of_cooperation(coop.id)
        assert len(plans) == 2
        assert plans.with_id(plan1.id)
        assert plans.with_id(plan2.id)
        assert not plans.with_id(plan3.id)

    def test_nothing_returned_when_no_plans_in_cooperation(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=None)
        plans = self.plan_repository.get_plans().that_are_part_of_cooperation(coop.id)
        assert len(plans) == 0

    def test_correct_inbound_requests_are_returned(self) -> None:
        coordinator = self.company_generator.create_company_entity()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        requesting_plan1 = self.plan_generator.create_plan(requested_cooperation=coop)
        requesting_plan2 = self.plan_generator.create_plan(requested_cooperation=coop)
        other_coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=other_coop)
        inbound_requests = (
            self.plan_repository.get_plans().that_request_cooperation_with_coordinator(
                coordinator.id
            )
        )
        assert len(inbound_requests) == 2
        assert requesting_plan1.id in map(lambda p: p.id, inbound_requests)
        assert requesting_plan2.id in map(lambda p: p.id, inbound_requests)

    def test_possible_to_add_and_to_remove_plan_to_cooperation(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan()

        self.plan_repository.get_plans().with_id(plan.id).update().set_cooperation(
            cooperation.id
        ).perform()
        plan_from_orm = self.plan_repository.get_plans().with_id(plan.id).first()
        assert plan_from_orm
        assert plan_from_orm.cooperation == cooperation.id

        self.plan_repository.get_plans().with_id(plan.id).update().set_cooperation(
            None
        ).perform()
        plan_from_orm = self.plan_repository.get_plans().with_id(plan.id).first()
        assert plan_from_orm
        assert plan_from_orm.cooperation is None

    def test_possible_to_set_and_unset_requested_cooperation_attribute(self):
        cooperation = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan()
        plan_result = self.plan_repository.get_plans().with_id(plan.id)
        plan_result.update().set_requested_cooperation(cooperation.id).perform()
        assert plan_result.that_request_cooperation_with_coordinator()
        plan_result.update().set_requested_cooperation(None).perform()
        assert not plan_result.that_request_cooperation_with_coordinator()

    def test_can_set_approval_date(self) -> None:
        plan = self.plan_generator.create_plan()
        plans = self.plan_repository.get_plans().with_id(plan.id)
        expected_approval_date = datetime(2000, 3, 2)
        assert plans.update().set_approval_date(expected_approval_date).perform()
        assert all(plan.approval_date == expected_approval_date for plan in plans)


class WherePayoutCountsAreLessThenActiveDaysTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.update_and_payout = self.injector.get(UpdatePlansAndPayout)

    def test_that_plan_is_included_in_results_if_two_days_have_passed_since_activation_and_no_certs_have_been_paid_out(
        self,
    ) -> None:
        now = datetime(2000, 1, 1)
        self.datetime_service.freeze_time(now)
        self.plan_generator.create_plan()
        query = self.plan_repository.get_plans()
        assert query.where_payout_counts_are_less_then_active_days(
            now + timedelta(days=2)
        )

    def test_that_plan_is_not_included_in_results_if_two_days_have_passed_and_certificates_have_been_payed_out(
        self,
    ) -> None:
        plan_creation = datetime(2000, 1, 1)
        self.datetime_service.freeze_time(plan_creation)
        self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=2))
        self.update_and_payout()
        query = self.plan_repository.get_plans()
        assert not query.where_payout_counts_are_less_then_active_days(
            self.datetime_service.now()
        )

    def test_2_days_after_expiration_the_payout_count_is_still_not_less_then_active_days(
        self,
    ) -> None:
        plan_creation = datetime(2000, 1, 1)
        self.datetime_service.freeze_time(plan_creation)
        self.plan_generator.create_plan(timeframe=2)
        self.datetime_service.advance_time(timedelta(days=2))
        self.update_and_payout()
        self.datetime_service.advance_time(timedelta(days=2))
        query = self.plan_repository.get_plans()
        assert not query.where_payout_counts_are_less_then_active_days(
            self.datetime_service.now()
        )


class GetStatisticsTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_with_no_plans_that_average_planning_duration_is_0(self) -> None:
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.average_plan_duration_in_days == Decimal(0)

    def test_with_no_plans_that_planning_costs_are_0(self) -> None:
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.total_planned_costs == ProductionCosts.zero()

    def test_with_one_active_plan_that_average_duration_is_exactly_the_length_of_that_plan(
        self,
    ) -> None:
        self.plan_generator.create_plan(timeframe=3)
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.average_plan_duration_in_days == Decimal(3)

    def test_with_two_active_plans_the_average_duration_is_the_mean_of_those_plans(
        self,
    ) -> None:
        self.plan_generator.create_plan(timeframe=3)
        self.plan_generator.create_plan(timeframe=5)
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.average_plan_duration_in_days == Decimal(4)

    def test_with_one_active_plan_the_total_planned_costs_is_exactly_that_plans_cost(
        self,
    ) -> None:
        expected_costs = ProductionCosts(
            labour_cost=Decimal(4), resource_cost=Decimal(3), means_cost=Decimal(5)
        )
        self.plan_generator.create_plan(costs=expected_costs)
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.total_planned_costs == expected_costs

    def test_with_two_active_plans_the_total_planned_costs_is_exactly_the_sum_of_plans_costs(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(2),
                resource_cost=Decimal(6),
                labour_cost=Decimal(8),
            )
        )
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(3),
                resource_cost=Decimal(7),
                labour_cost=Decimal(9),
            )
        )
        stats = self.plan_repository.get_plans().get_statistics()
        assert stats.total_planned_costs == ProductionCosts(
            means_cost=Decimal(5),
            resource_cost=Decimal(13),
            labour_cost=Decimal(17),
        )


class ThatWereActivatedBeforeTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_plan_activated_before_a_specified_timestamp_are_included_in_the_result(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan()
        assert self.plan_repository.get_plans().that_were_activated_before(
            datetime(2000, 1, 2)
        )

    def test_plan_activated_exactly_at_a_specified_timestamp_are_included_in_the_result(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan()
        assert self.plan_repository.get_plans().that_were_activated_before(
            datetime(2000, 1, 1)
        )

    def test_plan_activated_after_a_specified_timestamp_are_excluded_from_result(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan()
        assert not self.plan_repository.get_plans().that_were_activated_before(
            datetime(1999, 12, 31)
        )


class ThatWillExpireAfterTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_plan_that_will_expire_after_specified_date_is_included_in_results(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        assert self.plan_repository.get_plans().that_will_expire_after(
            datetime(2000, 1, 1)
        )

    def test_that_plan_that_will_expire_exactly_at_specified_timestamp_is_not_included_in_results(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        assert not self.plan_repository.get_plans().that_will_expire_after(
            datetime(2000, 1, 2)
        )

    def test_plan_that_will_expire_before_specified_timestamp_is_not_included_in_result(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        assert not self.plan_repository.get_plans().that_will_expire_after(
            datetime(2000, 1, 3)
        )
