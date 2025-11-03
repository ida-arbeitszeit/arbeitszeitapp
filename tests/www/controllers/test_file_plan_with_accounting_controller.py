from uuid import uuid4

from arbeitszeit_web.www.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
)
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = FilePlanWithAccountingController()
        self.session.login_company(company=uuid4())

    def test_that_request_is_processed_as_invalid_with_empty_draft_id_string(
        self,
    ) -> None:
        draft_id = ""
        with self.assertRaises(FilePlanWithAccountingController.InvalidRequest):
            self.controller.process_file_plan_with_accounting_request(
                draft_id, self.session
            )

    def test_that_proper_interactor_request_is_returned_when_draft_id_is_a_uuid_string(
        self,
    ) -> None:
        draft_id = str(uuid4())
        self.controller.process_file_plan_with_accounting_request(
            draft_id, self.session
        )

    def test_that_invalid_request_is_returned_if_draft_id_string_is_not_a_valid_uuid(
        self,
    ) -> None:
        draft_id = "123"
        with self.assertRaises(FilePlanWithAccountingController.InvalidRequest):
            self.controller.process_file_plan_with_accounting_request(
                draft_id, self.session
            )

    def test_that_draft_id_in_request_matches_id_string_given(self) -> None:
        expected_uuid = uuid4()
        draft_id = str(expected_uuid)
        request = self.controller.process_file_plan_with_accounting_request(
            draft_id, self.session
        )
        self.assertEqual(
            request.draft_id,
            expected_uuid,
        )

    def test_that_filing_company_uuid_is_taken_from_session(self) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        request = self.controller.process_file_plan_with_accounting_request(
            str(uuid4()), self.session
        )
        self.assertEqual(
            request.filing_company,
            expected_user_id,
        )

    def test_that_invalid_request_is_raised_when_user_is_not_logged_in(self) -> None:
        self.session.logout()
        with self.assertRaises(FilePlanWithAccountingController.InvalidRequest):
            self.controller.process_file_plan_with_accounting_request(
                str(uuid4()), self.session
            )
