from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import get_draft_details
from arbeitszeit.use_cases.create_plan_draft import (
    CreatePlanDraft,
    RejectionReason,
    Request,
)

from .base_test_case import BaseTestCase

REQUEST = Request(
    planner=uuid4(),
    costs=ProductionCosts(
        Decimal(1),
        Decimal(1),
        Decimal(1),
    ),
    product_name="testproduct",
    production_unit="kg",
    production_amount=10,
    description="test description",
    is_public_service=False,
    timeframe_in_days=7,
)


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_plan_draft = self.injector.get(CreatePlanDraft)
        self.get_draft_details = self.injector.get(get_draft_details.GetDraftDetails)

    def test_that_plan_plan_details_can_be_accessed_after_draft_is_created(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner)
        response = self.create_plan_draft(request)
        assert not response.is_rejected
        assert response.draft_id
        assert self.get_draft_details(response.draft_id)

    def test_that_create_plan_returns_a_draft_id(self) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner)
        response = self.create_plan_draft(request)
        assert response.draft_id

    def test_that_create_plan_gets_rejected_with_non_existing_planner(self) -> None:
        request = replace(
            REQUEST,
            planner=uuid4(),
        )
        response = self.create_plan_draft(request)
        assert response.is_rejected
        assert response.rejection_reason == RejectionReason.planner_does_not_exist
        assert not response.draft_id

    def test_that_create_plan_gets_rejected_with_negative_production_costs(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        request = replace(
            REQUEST,
            planner=planner,
            costs=ProductionCosts(Decimal(-1), Decimal(-1), Decimal(-1)),
        )
        response = self.create_plan_draft(request)
        assert response.is_rejected
        assert response.rejection_reason == RejectionReason.negative_plan_input
        assert not response.draft_id

    def test_that_create_plan_gets_rejected_with_negative_production_amount(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner, production_amount=-1)
        response = self.create_plan_draft(request)
        assert response.is_rejected
        assert not response.draft_id

    def test_that_create_plan_gets_rejected_with_negative_timeframe(self) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner, timeframe_in_days=-1)
        response = self.create_plan_draft(request)
        assert response.is_rejected
        assert not response.draft_id

    def test_that_drafted_plan_has_same_planner_as_specified_on_creation(self) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner)
        response = self.create_plan_draft(request)
        assert response.draft_id
        details = self.get_draft_details(response.draft_id)
        assert details
        assert details.planner_id == planner
