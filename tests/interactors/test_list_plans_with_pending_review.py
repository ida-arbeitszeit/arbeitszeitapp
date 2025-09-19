from typing import Optional
from uuid import UUID

from arbeitszeit.interactors.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.interactors.list_plans_with_pending_review import (
    ListPlansWithPendingReviewInteractor,
)

from .base_test_case import BaseTestCase
from .dependency_injection import get_dependency_injector


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.interactor = self.injector.get(ListPlansWithPendingReviewInteractor)
        self.file_plan_with_accounting_interactor = self.injector.get(
            FilePlanWithAccounting
        )

    def test_that_no_plans_are_returned_if_none_was_created(self) -> None:
        request = ListPlansWithPendingReviewInteractor.Request()
        response = self.interactor.list_plans_with_pending_review(request=request)
        self.assertFalse(response.plans)

    def test_that_new_plan_with_pending_review_is_created_when_filing_a_draft(
        self,
    ) -> None:
        self.file_plan_draft()
        response = self.interactor.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertTrue(response.plans)

    def test_that_plan_id_of_newly_filed_plan_shows_up_in_listing(self) -> None:
        plan_id = self.file_plan_draft()
        response = self.interactor.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertIn(plan_id, [plan.id for plan in response.plans])

    def test_that_product_name_shows_up_correctly_for_listed_plans(self) -> None:
        expected_product_name = "my example product"
        self.file_plan_draft(product_name=expected_product_name)
        response = self.interactor.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertIn(
            expected_product_name, [plan.product_name for plan in response.plans]
        )

    def test_name_of_planning_company_is_in_reponse(self) -> None:
        expected_company_name = "example company name"
        planner = self.company_generator.create_company(name=expected_company_name)
        self.file_plan_draft(planner=planner)
        response = self.interactor.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertIn(
            expected_company_name, [plan.planner_name for plan in response.plans]
        )

    def test_id_of_planning_company_is_in_response(self) -> None:
        planner = self.company_generator.create_company()
        self.file_plan_draft(planner=planner)
        response = self.interactor.list_plans_with_pending_review(
            request=ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertIn(planner, [plan.planner_id for plan in response.plans])

    def file_plan_draft(
        self, product_name: Optional[str] = None, planner: Optional[UUID] = None
    ) -> UUID:
        if planner is None:
            planner = self.company_generator.create_company()
        if product_name is None:
            product_name = "test draft name"
        draft = self.plan_generator.draft_plan(
            product_name=product_name, planner=planner
        )
        request = FilePlanWithAccounting.Request(draft_id=draft, filing_company=planner)
        response = self.file_plan_with_accounting_interactor.file_plan_with_accounting(
            request
        )
        assert response.plan_id
        return response.plan_id
