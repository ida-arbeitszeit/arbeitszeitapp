from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.get_draft_details import (
    DraftDetailsResponse,
    DraftDetailsSuccess,
    GetDraftDetails,
)
from tests.data_generators import CompanyGenerator, PlanGenerator
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase
from .dependency_injection import injection_test


@injection_test
def test_that_correct_planner_id_is_returned(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    draft = plan_generator.draft_plan(planner=planner)
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.planner_id == planner)


@injection_test
def test_that_correct_production_costs_are_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
):
    draft = plan_generator.draft_plan(
        costs=ProductionCosts(
            means_cost=Decimal(1),
            labour_cost=Decimal(2),
            resource_cost=Decimal(3),
        )
    )
    details = get_draft_details(draft)
    assert_success(
        details,
        lambda s: all(
            [
                s.means_cost == Decimal(1),
                s.labour_cost == Decimal(2),
                s.resources_cost == Decimal(3),
            ]
        ),
    )


@injection_test
def test_that_correct_product_name_is_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
):
    draft = plan_generator.draft_plan(product_name="test product")
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.product_name == "test product")


@injection_test
def test_that_correct_product_description_is_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
):
    draft = plan_generator.draft_plan(description="test description")
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.description == "test description")


@injection_test
def test_that_correct_product_unit_is_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
):
    draft = plan_generator.draft_plan(production_unit="test unit")
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.production_unit == "test unit")


@injection_test
def test_that_correct_amount_is_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
):
    draft = plan_generator.draft_plan(amount=123)
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.amount == 123)


@injection_test
def test_that_correct_public_service_is_shown(
    plan_generator: PlanGenerator,
    get_draft_details: GetDraftDetails,
) -> None:
    draft = plan_generator.draft_plan(is_public_service=True)
    details = get_draft_details(draft)
    assert_success(details, lambda s: s.is_public_service == True)


@injection_test
def test_that_none_is_returned_when_draft_does_not_exist(
    get_draft_details: GetDraftDetails,
) -> None:
    assert get_draft_details(uuid4()) is None


class GetDraftDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_draft_details = self.injector.get(GetDraftDetails)

    @parameterized.expand(
        [
            (datetime_utc(2000, 1, 2),),
            (datetime_utc(2039, 1, 3),),
        ]
    )
    def test_that_creation_timestamp_is_time_of_request_1(
        self, expected_timestamp: datetime
    ) -> None:
        self.datetime_service.freeze_time(expected_timestamp)
        draft = self.plan_generator.draft_plan(is_public_service=True)
        self.datetime_service.advance_time(timedelta(days=1))
        details = self.get_draft_details(draft)
        assert_success(details, lambda s: s.creation_timestamp == expected_timestamp)


def assert_success(
    response: DraftDetailsResponse, assertion: Callable[[DraftDetailsSuccess], bool]
) -> None:
    assert isinstance(response, DraftDetailsSuccess)
    assert assertion(response)
