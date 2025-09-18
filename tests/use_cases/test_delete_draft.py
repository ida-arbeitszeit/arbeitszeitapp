from uuid import UUID, uuid4

from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit.use_cases.get_draft_details import GetDraftDetailsUseCase

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(DeleteDraftUseCase)
        self.get_draft_details = self.injector.get(GetDraftDetailsUseCase)

    def test_that_failure_is_raised_if_non_existing_plan_is_deleted_for_non_existing_company(
        self,
    ) -> None:
        with self.assertRaises(DeleteDraftUseCase.Failure):
            self.use_case.delete_draft(
                self.create_request(deleter=uuid4(), draft=uuid4())
            )

    def test_that_no_failure_is_raised_if_draft_is_deleted_by_its_owner(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(planner=planner)
        self.use_case.delete_draft(self.create_request(deleter=planner, draft=draft))

    def test_that_failure_is_raised_if_draft_does_not_exist(self) -> None:
        planner = self.company_generator.create_company()
        with self.assertRaises(DeleteDraftUseCase.Failure):
            self.use_case.delete_draft(
                self.create_request(deleter=planner, draft=uuid4()),
            )

    def test_that_failure_is_raised_if_company_does_not_exist(self) -> None:
        draft = self.plan_generator.draft_plan()
        with self.assertRaises(DeleteDraftUseCase.Failure):
            self.use_case.delete_draft(
                self.create_request(deleter=uuid4(), draft=draft),
            )

    def test_that_after_deleting_draft_details_is_not_available_anymore(self) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(planner=planner)
        self.use_case.delete_draft(self.create_request(deleter=planner, draft=draft))
        response = self.get_draft_details.execute(draft_id=draft)
        self.assertIsNone(response)

    def test_that_plan_is_not_deleted_if_deleter_is_not_planner(self) -> None:
        company = self.company_generator.create_company_record()
        draft = self.plan_generator.draft_plan()
        with self.assertRaises(DeleteDraftUseCase.Failure):
            self.use_case.delete_draft(
                self.create_request(deleter=company.id, draft=draft)
            )
        response = self.get_draft_details.execute(draft_id=draft)
        self.assertIsNotNone(response)

    def test_failure_is_raised_if_deleter_is_not_planner(self) -> None:
        company = self.company_generator.create_company_record()
        draft = self.plan_generator.draft_plan()
        with self.assertRaises(DeleteDraftUseCase.Failure):
            self.use_case.delete_draft(
                self.create_request(deleter=company.id, draft=draft)
            )

    def test_show_draft_name_in_successful_deletion_response(self) -> None:
        expected_name = "test product draft"
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(
            planner=planner, product_name=expected_name
        )
        response = self.use_case.delete_draft(
            self.create_request(deleter=planner, draft=draft)
        )
        self.assertEqual(response.product_name, expected_name)

    def create_request(self, deleter: UUID, draft: UUID) -> DeleteDraftUseCase.Request:
        return DeleteDraftUseCase.Request(
            deleter=deleter,
            draft=draft,
        )
