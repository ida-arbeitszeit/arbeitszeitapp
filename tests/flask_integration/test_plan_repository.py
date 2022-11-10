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

    def test_active_plans_are_counted_correctly(self) -> None:
        assert self.plan_repository.count_active_plans() == 0
        self.plan_generator.create_plan(activation_date=datetime.min)
        self.plan_generator.create_plan(activation_date=datetime.min)
        assert self.plan_repository.count_active_plans() == 2

    def test_active_public_plans_are_counted_correctly(self) -> None:
        assert self.plan_repository.count_active_public_plans() == 0
        self.plan_generator.create_plan(
            activation_date=datetime.min, is_public_service=True
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min, is_public_service=True
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min, is_public_service=False
        )
        assert self.plan_repository.count_active_public_plans() == 2

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

    def test_three_active_plans_get_retrieved_ordered_by_activation_date(self) -> None:
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
            self.plan_repository.get_three_latest_active_plans_ordered_by_activation_date()
        )
        assert len(retrieved_plans) == 3
        assert retrieved_plans[0] == plans[1]
        assert retrieved_plans[1] == plans[2]
        assert retrieved_plans[2] == plans[4]

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

    def test_that_all_plans_for_a_company_are_returned(self) -> None:
        company = self.company_generator.create_company_entity()
        self.plan_generator.create_plan(planner=company, activation_date=None)
        self.plan_generator.create_plan(planner=company, is_public_service=True)
        self.plan_generator.create_plan(planner=company, is_available=False)
        returned_plans = list(
            self.plan_repository.get_all_plans_for_company_descending(
                company_id=company.id
            )
        )
        assert len(returned_plans) == 3

    def test_that_all_plans_for_a_company_are_returned_in_descending_order(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        third = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() - timedelta(days=1)
        )
        second = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() - timedelta(days=9)
        )
        first = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(datetime(2000, 1, 2))
        returned_plans = list(
            self.plan_repository.get_all_plans_for_company_descending(
                company_id=company.id
            )
        )
        assert returned_plans[0] == third
        assert returned_plans[1] == second
        assert returned_plans[2] == first

    def test_that_all_active_plan_for_a_company_are_returned(self) -> None:
        company = self.company_generator.create_company_entity()
        self.plan_generator.create_plan(planner=company)
        self.plan_generator.create_plan(planner=company)
        returned_plans = list(
            self.plan_repository.get_all_active_plans_for_company(company_id=company.id)
        )
        assert len(returned_plans) == 2

    def test_that_plan_gets_hidden(self) -> None:
        plan = self.plan_generator.create_plan()
        self.plan_repository.hide_plan(plan.id)
        plan_from_repo = self.plan_repository.get_plan_by_id(plan.id)
        assert plan_from_repo
        assert plan_from_repo.hidden_by_user

    def test_that_query_active_plans_by_exact_product_name_returns_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan(
            activation_date=datetime.min, product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.query_active_plans_by_product_name("Delivery of goods")
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_query_active_plans_by_substring_of_product_name_returns_plan(
        self,
    ) -> None:
        expected_plan = self.plan_generator.create_plan(
            activation_date=datetime.min, product_name="Delivery of goods"
        )
        returned_plan = list(
            self.plan_repository.query_active_plans_by_product_name("very of go")
        )
        assert returned_plan
        assert returned_plan[0] == expected_plan

    def test_that_query_active_plans_by_substring_of_plan_id_returns_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan(activation_date=datetime.min)
        expected_plan_id = expected_plan.id
        query = str(expected_plan_id)[3:8]
        returned_plan = list(self.plan_repository.query_active_plans_by_plan_id(query))
        assert returned_plan
        assert returned_plan[0] == expected_plan

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

    def test_that_all_productive_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
        self,
    ) -> None:
        assert not list(
            self.plan_repository.all_productive_plans_approved_active_and_not_expired()
        )

    def test_all_public_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
        self,
    ) -> None:
        assert not list(
            self.plan_repository.all_public_plans_approved_active_and_not_expired()
        )

    def test_all_plans_approved_active_and_not_expired_returns_no_plans_with_empty_db(
        self,
    ) -> None:
        assert not list(
            self.plan_repository.all_plans_approved_active_and_not_expired()
        )

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
