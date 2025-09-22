from typing import Callable, Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit.interactors.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit.interactors.list_plans_with_pending_review import (
    ListPlansWithPendingReviewInteractor,
)
from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.plan_details import PlanDetails

from .base_test_case import BaseTestCase


class BaseInteractorTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(FilePlanWithAccounting)
        self.list_plans_with_pending_review_interactor = self.injector.get(
            ListPlansWithPendingReviewInteractor
        )
        self.get_plan_details_interactor = self.injector.get(GetPlanDetailsInteractor)
        self.planner = self.company_generator.create_company()

    def file_draft(self, draft: UUID) -> UUID:
        request = self.create_request(draft=draft)
        response = self.interactor.file_plan_with_accounting(request)
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
        return draft

    def create_request(
        self,
        draft: Optional[UUID] = None,
        filing_company: Optional[UUID] = None,
    ) -> FilePlanWithAccounting.Request:
        if filing_company is None:
            filing_company = self.planner
        if draft is None:
            draft = self.create_draft()
        return FilePlanWithAccounting.Request(
            draft_id=draft, filing_company=filing_company
        )

    def assertPlanDetailsIsAvailable(self, plan: UUID) -> None:
        request = GetPlanDetailsInteractor.Request(plan)
        response = self.get_plan_details_interactor.get_plan_details(request)
        self.assertTrue(
            response,
            msg=f"Plan details for plan {plan} is not available",
        )

    def assertPlanDetails(
        self, plan: UUID, condition: Callable[[PlanDetails], bool]
    ) -> None:
        request = GetPlanDetailsInteractor.Request(plan)
        response = self.get_plan_details_interactor.get_plan_details(request)
        self.assertTrue(
            response,
            msg=f"Plan details for plan {plan} is not available",
        )
        assert response
        details = response.plan_details
        self.assertTrue(condition(details), msg=f"{details}")


class InteractorTests(BaseInteractorTestCase):
    def test_that_filing_a_plan_with_a_random_draft_id_is_rejected(self) -> None:
        request = self.create_request(draft=uuid4())
        response = self.interactor.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_can_file_a_regular_plan_draft_with_accounting(self) -> None:
        request = self.create_request()
        response = self.interactor.file_plan_with_accounting(request)
        self.assertTrue(response.is_plan_successfully_filed)

    def test_that_the_same_draft_cannot_be_filed_twice(self) -> None:
        request = self.create_request()
        self.interactor.file_plan_with_accounting(request)
        response = self.interactor.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_that_response_contains_a_plan_id_when_a_valid_draft_is_provided(
        self,
    ) -> None:
        request = self.create_request()
        response = self.interactor.file_plan_with_accounting(request)
        self.assertIsNotNone(response.plan_id)

    def test_that_response_does_not_contain_plan_id_if_no_valid_draft_was_provided(
        self,
    ) -> None:
        request = self.create_request(draft=uuid4())
        response = self.interactor.file_plan_with_accounting(request)
        self.assertIsNone(response.plan_id)

    def test_that_we_can_retrieve_plan_details_for_a_plan_that_was_filed(self) -> None:
        request = self.create_request()
        response = self.interactor.file_plan_with_accounting(request)
        assert response.plan_id
        self.assertPlanDetailsIsAvailable(plan=response.plan_id)

    def test_that_product_name_is_correct_in_newly_created_plan(self) -> None:
        expected_product_name = "test product name"
        draft = self.create_draft(product_name=expected_product_name)
        plan_id = self.file_draft(draft)
        self.assertPlanDetails(
            plan=plan_id,
            condition=lambda s: s.product_name == expected_product_name,
        )

    def test_if_company_that_is_not_creator_of_craft_tries_to_file_a_draft_then_it_does_not_show_in_list_of_pending_reviews(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_record()
        request = self.create_request(draft=draft, filing_company=other_company.id)
        self.interactor.file_plan_with_accounting(request)
        response = self.list_plans_with_pending_review_interactor.list_plans_with_pending_review(
            ListPlansWithPendingReviewInteractor.Request()
        )
        self.assertFalse(response.plans)

    def test_if_company_that_is_not_creator_of_craft_tries_to_file_a_draft_then_plan_is_not_filed_successfully(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_record()
        request = self.create_request(draft=draft, filing_company=other_company.id)
        response = self.interactor.file_plan_with_accounting(request)
        self.assertFalse(response.is_plan_successfully_filed)

    def test_that_original_planner_can_stil_file_draft_after_other_company_tried_to_file_it(
        self,
    ) -> None:
        draft = self.create_draft()
        other_company = self.company_generator.create_company_record()
        self.interactor.file_plan_with_accounting(
            request=self.create_request(draft=draft, filing_company=other_company.id)
        )
        response = self.interactor.file_plan_with_accounting(
            request=self.create_request(
                draft=draft,
                filing_company=self.planner,
            )
        )
        self.assertTrue(
            response.is_plan_successfully_filed,
        )

    def test_cannot_file_plan_if_planner_is_not_confirmed(self) -> None:
        planner = self.company_generator.create_company(confirmed=False)
        draft = self.plan_generator.draft_plan(planner=planner)
        request = self.create_request(draft=draft, filing_company=planner)
        response = self.interactor.file_plan_with_accounting(request)
        assert not response.is_plan_successfully_filed


class NotificationTests(BaseInteractorTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_that_accountants_are_notified_about_new_plan_on_success(self) -> None:
        self.accountant_generator.create_accountant()
        self.interactor.file_plan_with_accounting(request=self.create_request())
        self.assertTrue(self.get_sent_accountant_notifications())

    def test_that_notification_to_accountants_contains_correct_product_name(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        expected_product_name = "test product name 53"
        self.interactor.file_plan_with_accounting(
            request=self.create_request(
                draft=self.create_draft(product_name=expected_product_name)
            )
        )
        latest_notification = self.email_sender.get_latest_message_sent()
        assert isinstance(
            latest_notification,
            email_notifications.AccountantNotificationAboutNewPlan,
        )
        self.assertEqual(
            latest_notification.product_name,
            expected_product_name,
        )

    def test_that_notification_contains_correct_plan_id(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        response = self.interactor.file_plan_with_accounting(
            request=self.create_request()
        )
        latest_notification = self.email_sender.get_latest_message_sent()
        assert isinstance(
            latest_notification,
            email_notifications.AccountantNotificationAboutNewPlan,
        )
        self.assertEqual(
            latest_notification.plan_id,
            response.plan_id,
        )

    def test_that_with_two_accountants_two_notifications_are_sent_out(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        self.accountant_generator.create_accountant()
        self.interactor.file_plan_with_accounting(request=self.create_request())
        assert len(self.get_sent_accountant_notifications()) == 2

    def test_that_with_three_accountants_three_notifications_are_sent_out(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        self.accountant_generator.create_accountant()
        self.accountant_generator.create_accountant()
        self.interactor.file_plan_with_accounting(request=self.create_request())
        assert len(self.get_sent_accountant_notifications()) == 3

    @parameterized.expand(
        [
            ("test accountant name",),
            ("other accountant name",),
        ]
    )
    def test_that_accountant_is_addressed_by_their_correct_name(
        self, expected_name: str
    ) -> None:
        self.accountant_generator.create_accountant(name=expected_name)
        self.interactor.file_plan_with_accounting(request=self.create_request())
        assert (
            self.get_latest_accountant_notification().accountant_name == expected_name
        )

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_notifiations_are_sent_to_accountant_email_address(
        self, expected_email_address: str
    ) -> None:
        self.accountant_generator.create_accountant(
            email_address=expected_email_address
        )
        self.interactor.file_plan_with_accounting(request=self.create_request())
        assert (
            self.get_latest_accountant_notification().accountant_email_address
            == expected_email_address
        )

    def get_sent_accountant_notifications(
        self,
    ) -> list[email_notifications.AccountantNotificationAboutNewPlan]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.AccountantNotificationAboutNewPlan)
        ]

    def get_latest_accountant_notification(
        self,
    ) -> email_notifications.AccountantNotificationAboutNewPlan:
        notifications = self.get_sent_accountant_notifications()
        assert notifications
        return notifications[-1]
