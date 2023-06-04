from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases.create_plan_draft import (
    CreatePlanDraft,
    CreatePlanDraftRequest,
    CreatePlanDraftResponse,
)

from .base_test_case import BaseTestCase
from .repositories import PlanDraftRepository

REQUEST = CreatePlanDraftRequest(
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
        self.plan_draft_repository = self.injector.get(PlanDraftRepository)

    def test_that_create_plan_creates_a_plan_draft_that_is_not_rejected(self) -> None:
        planner = self.company_generator.create_company()
        request = replace(REQUEST, planner=planner)
        assert not self.plan_draft_repository.get_plan_drafts()
        response = self.create_plan_draft(request)
        assert len(self.plan_draft_repository.get_plan_drafts()) == 1
        assert not response.is_rejected

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
        assert (
            response.rejection_reason
            == CreatePlanDraftResponse.RejectionReason.planner_does_not_exist
        )
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
        assert (
            response.rejection_reason
            == CreatePlanDraftResponse.RejectionReason.negative_plan_input
        )
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
        draft = self.plan_generator.draft_plan(planner=planner)
        assert draft.planner == planner
