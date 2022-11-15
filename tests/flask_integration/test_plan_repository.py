from datetime import datetime, timedelta
from decimal import Decimal
from typing import Union
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit_flask.database.repositories import PlanRepository
from tests.datetime_service import FakeDatetimeService

from ..data_generators import CompanyGenerator, PlanGenerator
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

    def test_avg_timeframe_of_active_plans_is_calculated_correctly(self) -> None:
        assert self.plan_repository.avg_timeframe_of_active_plans() == 0
        self.plan_generator.create_plan(timeframe=5)
        self.plan_generator.create_plan(timeframe=3)
        assert self.plan_repository.avg_timeframe_of_active_plans() == 4

    def test_sum_of_active_planned_work_calculated_correctly(self) -> None:
        assert self.plan_repository.sum_of_active_planned_work() == 0
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(2, 0, 0),
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(3, 0, 0),
        )
        assert self.plan_repository.sum_of_active_planned_work() == 5

    def test_sum_of_active_planned_resources_calculated_correctly(self) -> None:
        assert self.plan_repository.sum_of_active_planned_resources() == 0
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(0, 2, 0),
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(0, 3, 0),
        )
        assert self.plan_repository.sum_of_active_planned_resources() == 5

    def test_sum_of_active_planned_means_calculated_correctly(self) -> None:
        assert self.plan_repository.sum_of_active_planned_means() == 0
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(0, 0, 2),
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min,
            costs=production_costs(0, 0, 3),
        )
        assert self.plan_repository.sum_of_active_planned_means() == 5

    def test_all_active_plans_get_retrieved(self) -> None:
        number_of_plans = 5
        list_of_plans = [
            self.plan_generator.create_plan(activation_date=datetime.min)
            for _ in range(number_of_plans)
        ]
        retrieved_plans = list(self.plan_repository.get_active_plans())
        assert len(retrieved_plans) == number_of_plans
        for plan in list_of_plans:
            assert plan in retrieved_plans

    def test_plans_that_were_set_to_expired_dont_show_up_in_active_plans(self) -> None:
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        assert plan in list(self.plan_repository.get_active_plans())
        self.plan_repository.set_plan_as_expired(plan)
        assert plan not in list(self.plan_repository.get_active_plans())

    def test_get_plan_by_id_with_unkown_id_results_in_none(self) -> None:
        assert self.plan_repository.get_plan_by_id(uuid4()) is None

    def test_that_existing_plan_can_be_retrieved_by_id(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        assert expected_plan == self.plan_repository.get_plan_by_id(expected_plan.id)

    def test_that_plan_gets_hidden(self) -> None:
        plan = self.plan_generator.create_plan()
        self.plan_repository.hide_plan(plan.id)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.hidden_by_user

    def test_that_active_days_are_set(self) -> None:
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        assert plan.active_days is None
        self.plan_repository.set_active_days(plan, 3)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.active_days == 3

    def test_that_payout_count_is_increased_by_one(self) -> None:
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        assert plan.payout_count == 0
        self.plan_repository.increase_payout_count_by_one(plan)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.payout_count == 1

    def test_that_availability_is_toggled_to_false(self) -> None:
        plan = self.plan_generator.create_plan()
        assert plan.is_available == True
        self.plan_repository.toggle_product_availability(plan)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.is_available == False

    def test_that_availability_is_toggled_to_true(self) -> None:
        plan = self.plan_generator.create_plan(is_available=False)
        assert plan.is_available == False
        self.plan_repository.toggle_product_availability(plan)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.is_available == True

    def test_correct_name_and_description_returned(self) -> None:
        expected_name = "name 20220621"
        expected_description = "description 20220621"
        plan = self.plan_generator.create_plan(
            product_name=expected_name, description=expected_description
        )
        plan_info = self.plan_repository.get_plan_name_and_description(plan.id)
        assert plan_info.name == expected_name
        assert plan_info.description == expected_description

    def test_that_non_existing_plan_returns_no_planner_id(self) -> None:
        self.plan_generator.create_plan()
        nothing = self.plan_repository.get_planner_id(uuid4())
        assert nothing is None

    def test_that_correct_id_of_planning_company_gets_returned(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        plan_id = self.plan_repository.get_planner_id(expected_plan.id)
        assert plan_id == expected_plan.planner.id

    def test_cannot_create_plan_from_non_existing_draft(self) -> None:
        assert self.plan_repository.create_plan_from_draft(uuid4()) is None

    def test_can_create_plan_from_exiting_draft(self) -> None:
        draft = self.plan_generator.draft_plan()
        assert self.plan_repository.create_plan_from_draft(draft.id) is not None

    def test_query_plan_after_it_was_created_from_draft(self) -> None:
        draft = self.plan_generator.draft_plan()
        plan_id = self.plan_repository.create_plan_from_draft(draft.id)
        assert plan_id
        assert self.plan_repository.get_plan_by_id(plan_id) is not None


class GetActivePlansTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_active_plans_can_be_ordered_by_creation_date_in_descending_order(
        self,
    ) -> None:
        activation_dates = [
            self.datetime_service.now_minus_ten_days(),
            self.datetime_service.now(),
            self.datetime_service.now_minus_20_hours(),
            self.datetime_service.now_minus_25_hours(),
            self.datetime_service.now_minus_one_day(),
        ]
        plans = [
            self.plan_generator.create_plan(activation_date=date)
            for date in activation_dates
        ]
        retrieved_plans = list(
            self.plan_repository.get_active_plans()
            .ordered_by_creation_date(ascending=False)
            .limit(3)
        )
        assert len(retrieved_plans) == 3
        assert retrieved_plans[0] == plans[1]
        assert retrieved_plans[1] == plans[2]
        assert retrieved_plans[2] == plans[4]

    def test_that_active_plans_can_be_filtered_by_product_name(self) -> None:
        expected_plan = self.plan_generator.create_plan(
            activation_date=datetime.min, product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.get_active_plans().with_product_name_containing(
                "Delivery of goods"
            )
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_active_plans_can_be_filtered_by_substrings_of_product_name(
        self,
    ) -> None:
        expected_plan = self.plan_generator.create_plan(
            activation_date=datetime.min, product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.get_active_plans().with_product_name_containing(
                "very of go"
            )
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_query_active_plans_by_substring_of_plan_id_returns_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan(activation_date=datetime.min)
        expected_plan_id = expected_plan.id
        query = str(expected_plan_id)[3:8]
        returned_plan = list(
            self.plan_repository.get_active_plans().with_id_containing(query)
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan


class GetAllPlansWithoutCompletedReviewTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_cannot_find_any_plans_with_empty_db(self) -> None:
        self.assertFalse(
            list(self.plan_repository.get_all_plans_without_completed_review())
        )

    def test_return_at_least_one_plan_if_previously_a_plan_was_created_from_a_draft(
        self,
    ) -> None:
        draft = self.plan_generator.draft_plan()
        self.plan_repository.create_plan_from_draft(draft.id)
        self.assertTrue(
            list(self.plan_repository.get_all_plans_without_completed_review())
        )

    def test_return_no_plan_if_there_is_only_one_approved_plan_in_db(self) -> None:
        self.plan_generator.create_plan(approved=True)
        self.assertFalse(
            list(self.plan_repository.get_all_plans_without_completed_review())
        )


class GetAllPlans(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_repository = self.injector.get(PlanRepository)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_without_any_plans_nothing_is_returned(self) -> None:
        assert not list(self.plan_repository.get_all_plans())

    def test_that_unapproved_plans_are_returned(self) -> None:
        self.plan_generator.create_plan(approved=False)
        assert list(self.plan_repository.get_all_plans())

    def test_that_approved_plans_are_returned(self) -> None:
        self.plan_generator.create_plan(approved=True)
        assert list(self.plan_repository.get_all_plans())

    def test_that_can_filter_unapproved_plans_from_results(self) -> None:
        self.plan_generator.create_plan(approved=False)
        assert not list(self.plan_repository.get_all_plans().that_are_approved())

    def test_can_filter_public_plans(self) -> None:
        self.plan_generator.create_plan(is_public_service=False)
        assert not list(self.plan_repository.get_all_plans().that_are_public())
        self.plan_generator.create_plan(is_public_service=True)
        assert list(self.plan_repository.get_all_plans().that_are_public())

    def test_can_filter_productive_plans(self) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        assert not list(self.plan_repository.get_all_plans().that_are_productive())
        self.plan_generator.create_plan(is_public_service=False)
        assert list(self.plan_repository.get_all_plans().that_are_productive())

    def test_can_count_all_plans(self) -> None:
        self.plan_generator.create_plan()
        assert len(self.plan_repository.get_all_plans()) == 1
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        assert len(self.plan_repository.get_all_plans()) == 3

    def test_can_filter_by_planner(self) -> None:
        planner = self.company_generator.create_company_entity()
        self.plan_generator.create_plan()
        assert not self.plan_repository.get_all_plans().planned_by(planner.id)
        self.plan_generator.create_plan(planner=planner)
        assert self.plan_repository.get_all_plans().planned_by(planner.id)
