from datetime import datetime
from decimal import Decimal
from math import isclose

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.review_registered_consumptions import (
    RewiewRegisteredConsumptionsUseCase as UseCase,
)
from tests.use_cases.base_test_case import BaseTestCase


class ReviewRegisteredConsumptionsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.providing_company = self.company_generator.create_company()

    def test_empty_list_is_returned_when_no_consumptions_exist(self) -> None:
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert not response.consumptions

    def test_empty_list_is_returned_when_no_consumptions_of_product_of_specified_company_exist(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert not response.consumptions

    def test_one_consumption_is_returned_when_one_private_consumption_exists(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert len(response.consumptions) == 1

    def test_one_consumption_is_returned_when_one_fixed_means_consumption_exists(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert len(response.consumptions) == 1

    def test_one_consumption_is_returned_when_one_resource_consumption_exists(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert len(response.consumptions) == 1

    def test_two_consumptions_are_returned_when_one_private_and_one_fixed_means_consumption_exist(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(plan=plan)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert len(response.consumptions) == 2

    def test_three_consumptions_are_returned_in_descending_order_of_date(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(plan=plan)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert (
            response.consumptions[0].date
            > response.consumptions[1].date
            > response.consumptions[2].date
        )


class PrivateConsumptionDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.providing_company = self.company_generator.create_company()

    def test_private_consumption_shows_date_of_when_consumption_was_registered(
        self,
    ) -> None:
        expected_date = datetime(2019, 5, 1)
        self.datetime_service.freeze_time(expected_date)
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].date == expected_date

    def test_private_consumption_is_shown_as_private_consumption(self) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].is_private_consumption

    def test_private_consumer_name_is_shown(self) -> None:
        expected_consumer_name = "Test private consumer name"
        consumer = self.member_generator.create_member(name=expected_consumer_name)
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].consumer_name == expected_consumer_name

    def test_private_consumer_id_is_shown(self) -> None:
        expected_consumer_id = self.member_generator.create_member()
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_private_consumption(
            plan=plan, consumer=expected_consumer_id
        )
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].consumer_id == expected_consumer_id

    def test_product_name_is_shown(self) -> None:
        expected_product_name = "Test Product"
        plan = self.plan_generator.create_plan(
            planner=self.providing_company, product_name=expected_product_name
        )
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].product_name == expected_product_name

    def test_plan_id_is_shown(self) -> None:
        expected_plan_id = self.plan_generator.create_plan(
            planner=self.providing_company
        )
        self.consumption_generator.create_private_consumption(plan=expected_plan_id)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].plan_id == expected_plan_id

    def test_labour_hours_consumed_is_shown_that_equals_the_labour_costs_of_the_product(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].labour_hours_consumed == Decimal(6)

    def test_labour_hours_consumed_is_shown_that_equals_the_labour_costs_of_the_product_times_the_amount_consumed(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        self.consumption_generator.create_private_consumption(plan=plan, amount=2)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].labour_hours_consumed == Decimal(12)

    def test_labour_hours_consumed_is_shown_that_equals_the_cooperation_price_of_the_product_when_plan_is_cooperating(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        plan2 = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(4), Decimal(4), Decimal(4)),
            amount=1,
        )
        self.cooperation_generator.create_cooperation(plans=[plan1, plan2])

        self.consumption_generator.create_private_consumption(plan=plan1)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert isclose(response.consumptions[0].labour_hours_consumed, Decimal(9))


class ProductiveConsumptionDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.providing_company = self.company_generator.create_company()

    def test_productive_consumption_shows_date_of_when_consumption_was_registered(
        self,
    ) -> None:
        expected_date = datetime(2019, 5, 1)
        self.datetime_service.freeze_time(expected_date)
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].date == expected_date

    def test_consumption_of_fixed_means_of_production_shows_not_as_private_consumption(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert not response.consumptions[0].is_private_consumption

    def test_consumption_of_resources_shows_not_as_private_consumption(self) -> None:
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_resource_consumption_by_company(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert not response.consumptions[0].is_private_consumption

    def test_consumer_name_is_shown(self) -> None:
        expected_consumer_name = "Test consumer name"
        consumer = self.company_generator.create_company(name=expected_consumer_name)
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].consumer_name == expected_consumer_name

    def test_consumer_id_is_shown(self) -> None:
        expected_consumer_id = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=self.providing_company)
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=expected_consumer_id
        )
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].consumer_id == expected_consumer_id

    def test_product_name_is_shown(self) -> None:
        expected_product_name = "Test Product"
        plan = self.plan_generator.create_plan(
            planner=self.providing_company, product_name=expected_product_name
        )
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].product_name == expected_product_name

    def test_plan_id_is_shown(self) -> None:
        expected_plan_id = self.plan_generator.create_plan(
            planner=self.providing_company
        )
        self.consumption_generator.create_fixed_means_consumption(plan=expected_plan_id)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].plan_id == expected_plan_id

    def test_labour_hours_consumed_is_shown_that_equals_the_labour_costs_of_the_product(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].labour_hours_consumed == Decimal(6)

    def test_labour_hours_consumed_is_shown_that_equals_the_labour_costs_of_the_product_times_the_amount_consumed(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(plan=plan, amount=2)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert response.consumptions[0].labour_hours_consumed == Decimal(12)

    def test_labour_hours_consumed_is_shown_that_equals_the_cooperation_price_of_the_product_when_plan_is_cooperating(
        self,
    ) -> None:
        plan1 = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
            amount=1,
        )
        plan2 = self.plan_generator.create_plan(
            planner=self.providing_company,
            costs=ProductionCosts(Decimal(4), Decimal(4), Decimal(4)),
            amount=1,
        )
        self.cooperation_generator.create_cooperation(plans=[plan1, plan2])

        self.consumption_generator.create_fixed_means_consumption(plan=plan1)
        response = self.use_case.review_registered_consumptions(
            request=UseCase.Request(providing_company=self.providing_company)
        )
        assert isclose(response.consumptions[0].labour_hours_consumed, Decimal(9))
