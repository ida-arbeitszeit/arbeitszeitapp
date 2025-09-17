from decimal import Decimal
from typing import Callable, Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import edit_draft
from arbeitszeit.use_cases.get_draft_details import (
    DraftDetailsSuccess,
    GetDraftDetailsUseCase,
)
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(edit_draft.EditDraftUseCase)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.get_draft_details_use_case = self.injector.get(GetDraftDetailsUseCase)

    def test_cannot_edit_successfully_non_existing_draft(self) -> None:
        request = self.create_request(draft=uuid4())
        response = self.use_case.edit_draft(request)
        assert (
            response.rejection_reason == edit_draft.Response.RejectionReason.NOT_FOUND
        )

    def test_planner_can_edit_successfully_an_existing_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(planner=planner)
        request = self.create_request(draft=draft, editor=planner)
        response = self.use_case.edit_draft(request)
        assert not response.rejection_reason

    def test_non_planner_cannot_edit_draft_successfully(self) -> None:
        other_company = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan()
        request = self.create_request(draft=draft, editor=other_company)
        response = self.use_case.edit_draft(request)
        assert (
            response.rejection_reason
            == edit_draft.Response.RejectionReason.UNAUTHORIZED
        )

    def test_can_change_product_name_in_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner, product_name="original name"
        )
        request = self.create_request(
            draft=draft, editor=planner, product_name="new name"
        )
        self.use_case.edit_draft(request)
        self.assertDraft(
            draft,
            lambda d: d.product_name == "new name",
        )

    def test_can_change_labour_cost_in_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal("1"),
                resource_cost=Decimal("1"),
                means_cost=Decimal("1"),
            ),
        )
        request = self.create_request(
            draft=draft, editor=planner, labour_cost=Decimal(2)
        )
        self.use_case.edit_draft(request)
        self.assertDraft(
            draft,
            lambda d: d.labour_cost == Decimal(2),
        )

    def test_can_change_means_cost_in_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal("1"),
                resource_cost=Decimal("1"),
                means_cost=Decimal("1"),
            ),
        )
        request = self.create_request(
            draft=draft, editor=planner, means_cost=Decimal(2)
        )
        self.use_case.edit_draft(request)
        self.assertDraft(
            draft,
            lambda d: d.means_cost == Decimal(2),
        )

    def test_can_change_resource_cost_in_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal("1"),
                means_cost=Decimal("1"),
                resource_cost=Decimal("1"),
            ),
        )
        request = self.create_request(
            draft=draft, editor=planner, resource_cost=Decimal(2)
        )
        self.use_case.edit_draft(request)
        self.assertDraft(
            draft,
            lambda d: d.resources_cost == Decimal(2),
        )

    def test_can_change_description_in_draft(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            description="old description",
        )
        request = self.create_request(
            draft=draft, editor=planner, description="new description"
        )
        self.use_case.edit_draft(request)
        self.assertDraft(
            draft,
            lambda d: d.description == "new description",
        )

    def test_can_change_draft_from_public_to_productive(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            is_public_service=True,
        )
        request = self.create_request(
            draft=draft,
            editor=planner,
            is_public_service=False,
        )
        self.use_case.edit_draft(request)
        self.assertDraft(draft, lambda d: not d.is_public_service)

    def test_can_edit_timeframe(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            timeframe=1,
        )
        request = self.create_request(
            draft=draft,
            editor=planner,
            timeframe=2,
        )
        self.use_case.edit_draft(request)
        self.assertDraft(draft, lambda d: d.timeframe == 2)

    def test_can_change_unit_of_distribution(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner,
            production_unit="old unit",
        )
        request = self.create_request(
            draft=draft,
            editor=planner,
            unit_of_distribution="new unit",
        )
        self.use_case.edit_draft(request)
        self.assertDraft(draft, lambda d: d.production_unit == "new unit")

    def assertDraft(
        self, draft_id: UUID, condition: Callable[[DraftDetailsSuccess], bool]
    ) -> None:
        response = self.get_draft_details_use_case.execute(draft_id)
        assert isinstance(response, DraftDetailsSuccess)
        self.assertTrue(condition(response))

    def create_request(
        self,
        draft: UUID,
        editor: Optional[UUID] = None,
        product_name: Optional[str] = None,
        amount: Optional[int] = None,
        description: Optional[str] = None,
        labour_cost: Optional[Decimal] = None,
        means_cost: Optional[Decimal] = None,
        resource_cost: Optional[Decimal] = None,
        is_public_service: Optional[bool] = None,
        timeframe: Optional[int] = None,
        unit_of_distribution: Optional[str] = None,
    ) -> edit_draft.Request:
        if editor is None:
            editor = uuid4()
        return edit_draft.Request(
            draft=draft,
            editor=editor,
            product_name=product_name,
            amount=amount,
            description=description,
            labour_cost=labour_cost,
            means_cost=means_cost,
            resource_cost=resource_cost,
            is_public_service=is_public_service,
            timeframe=timeframe,
            unit_of_distribution=unit_of_distribution,
        )
