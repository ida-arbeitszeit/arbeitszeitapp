from typing import Callable, Optional, cast
from uuid import UUID, uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)

from .base_test_case import BaseTestCase
from .notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)


class BaseUseCaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(FilePlanWithAccounting)
        self.list_plans_with_pending_review_use_case = self.injector.get(
            ListPlansWithPendingReviewUseCase
        )
        self.get_plan_summary_member_use_case = self.injector.get(GetPlanSummaryMember)
        self.planner = self.company_generator.create_company_entity()
        self.notify_accountants_presenter = self.injector.get(
            NotifyAccountantsAboutNewPlanPresenterImpl
        )

    def file_draft(self, draft: UUID) -> UUID:
        request = self.create_request(draft=draft)
        response = self.use_case.file_plan_with_accounting(request)
        assert response.plan_id
        return response.plan_id

    def create_draft(
        self,
        product_name: Optional[str] = None,
        description: Optional[str] = None,
        costs: Optional[ProductionCosts] = None,
        production_unit: Optional[str] = None,
        amount: Optional[int] = None,
        is_public_service: Optional[bool] = None,
        timeframe: Optional[int] = None,
    ) -> UUID:
        draft = self.plan_generator.draft_plan(
            product_name=product_name,
            description=description,
            costs=costs,
            production_unit=production_unit,
            amount=amount,
            is_public_service=is_public_service,
            timeframe=timeframe,
            planner=self.planner,
        )
        return draft.id

    def create_request(
        self,
        draft: Optional[UUID] = None,
        filing_company: Optional[UUID] = None,
    ) -> FilePlanWithAccounting.Request:
        if filing_company is None:
            filing_company = self.planner.id
        if draft is None:
            draft = self.create_draft()
        return FilePlanWithAccounting.Request(
            draft_id=draft, filing_company=filing_company
        )

    def assertPlanSummaryIsAvailable(self, plan: UUID) -> None:
        response = self.get_plan_summary_member_use_case(plan_id=plan)
        self.assertIsInstance(
            response,
            GetPlanSummaryMember.Success,
            msg=f"Plan summary for plan {plan} is not available",
        )

    def assertPlanSummary(
        self, plan: UUID, condition: Callable[[PlanSummary], bool]
    ) -> None:
        response = self.get_plan_summary_member_use_case(plan_id=plan)
        self.assertIsInstance(
            response,
            GetPlanSummaryMember.Success,
            msg=f"Plan summary for plan {plan} is not available",
        )
        summary = cast(GetPlanSummaryMember.Success, response).plan_summary
        self.assertTrue(condition(summary), msg=f"{summary}")


class UseCaseTests(BaseUseCaseTestCase):
    def test_that_filing_a_plan_with_a_random_draft_id_is_rejected(self) -> None:
        request = self.create_request(draft=uuid4())
        response = self.use_case.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_can_file_a_regular_plan_draft_with_accounting(self) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        self.assertTrue(response.is_plan_successfully_filed)

    def test_that_the_same_draft_cannot_be_filed_twice(self) -> None:
        request = self.create_request()
        self.use_case.file_plan_with_accounting(request)
        response = self.use_case.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_that_response_contains_a_plan_id_when_a_valid_draft_is_provided(
        self,
    ) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        self.assertIsNotNone(response.plan_id)

    def test_that_response_does_not_contain_plan_id_if_no_valid_draft_was_provided(
        self,
    ) -> None:
        request = self.create_request(draft=uuid4())
        response = self.use_case.file_plan_with_accounting(request)
        self.assertIsNone(response.plan_id)

    def test_that_we_can_retrieve_plan_details_for_a_plan_that_was_filed(self) -> None:
        request = self.create_request()
        response = self.use_case.file_plan_with_accounting(request)
        assert response.plan_id
        self.assertPlanSummaryIsAvailable(plan=response.plan_id)

    def test_that_product_name_is_correct_in_newly_created_plan(self) -> None:
        expected_product_name = "test product name"
        draft = self.create_draft(product_name=expected_product_name)
        plan_id = self.file_draft(draft)
        self.assertPlanSummary(
            plan=plan_id,
            condition=lambda s: s.product_name == expected_product_name,
        )

    def test_if_company_that_is_not_creator_of_craft_tries_to_file_a_draft_then_it_does_not_show_in_list_of_pending_reviews(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_entity()
        request = self.create_request(draft=draft, filing_company=other_company.id)
        self.use_case.file_plan_with_accounting(request)
        response = (
            self.list_plans_with_pending_review_use_case.list_plans_with_pending_review(
                ListPlansWithPendingReviewUseCase.Request()
            )
        )
        self.assertFalse(response.plans)

    def test_if_company_that_is_not_creator_of_craft_tries_to_file_a_draft_then_plan_is_not_filed_successfully(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_entity()
        request = self.create_request(draft=draft, filing_company=other_company.id)
        response = self.use_case.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_that_original_planner_can_stil_file_draft_after_other_company_tried_to_file_it(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_entity()
        self.use_case.file_plan_with_accounting(
            request=self.create_request(draft=draft, filing_company=other_company.id)
        )
        response = self.use_case.file_plan_with_accounting(
            request=self.create_request(
                draft=draft,
                filing_company=self.planner.id,
            )
        )
        self.assertTrue(
            response.is_plan_successfully_filed,
        )


class NotificationTests(BaseUseCaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = self.accountant_generator.create_accountant()

    def test_that_accountants_are_notified_about_new_plan_on_success(self) -> None:
        self.use_case.file_plan_with_accounting(request=self.create_request())
        self.assertTrue(self.notify_accountants_presenter.sent_notifications)
        self.accountant_generator.create_accountant()

    def test_that_notification_to_accountants_contains_correct_product_name(
        self,
    ) -> None:
        expected_product_name = "test product name 53"
        self.use_case.file_plan_with_accounting(
            request=self.create_request(
                draft=self.create_draft(product_name=expected_product_name)
            )
        )
        self.assertEqual(
            self.notify_accountants_presenter.latest_notification.product_name,
            expected_product_name,
        )

    def test_that_notification_contains_correct_plan_id(
        self,
    ) -> None:
        response = self.use_case.file_plan_with_accounting(
            request=self.create_request()
        )
        self.assertEqual(
            self.notify_accountants_presenter.latest_notification.plan_id,
            response.plan_id,
        )

    def test_that_with_two_accountants_two_notifications_are_sent_out(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        self.use_case.file_plan_with_accounting(request=self.create_request())
        assert len(self.notify_accountants_presenter.sent_notifications) == 2

    def test_that_with_three_accountants_three_notifications_are_sent_out(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        self.accountant_generator.create_accountant()
        self.use_case.file_plan_with_accounting(request=self.create_request())
        assert len(self.notify_accountants_presenter.sent_notifications) == 3

    def test_that_notifications_are_sent_to_correct_user(self) -> None:
        self.use_case.file_plan_with_accounting(request=self.create_request())
        assert (
            self.notify_accountants_presenter.latest_notification.accountant_id
            == self.accountant
        )
