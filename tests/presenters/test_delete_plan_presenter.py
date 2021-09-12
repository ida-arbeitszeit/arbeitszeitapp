from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.delete_plan import DeletePlanResponse
from arbeitszeit_web.delete_plan import DeletePlanPresenter

SUCCESSFUL_DELETE_RESPONSE = DeletePlanResponse(
    plan_id=uuid4(),
    is_success=True,
)
FAILED_DELETE_RESPONSE = DeletePlanResponse(
    plan_id=uuid4(),
    is_success=False,
)


class DeletePlanPresenterTests(TestCase):
    def setUp(self):
        self.presenter = DeletePlanPresenter()

    def test_that_a_notification_is_shown_when_deletion_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_DELETE_RESPONSE)
        self.assertTrue(presentation.notifications)

    def test_that_no_notification_is_shown_when_deletion_was_a_failure(self):
        presentation = self.presenter.present(FAILED_DELETE_RESPONSE)
        self.assertFalse(presentation.notifications)
