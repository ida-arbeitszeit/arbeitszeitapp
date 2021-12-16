from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.hide_plan import HidePlanResponse
from arbeitszeit_web.hide_plan import HidePlanPresenter

SUCCESSFUL_DELETE_RESPONSE = HidePlanResponse(
    plan_id=uuid4(),
    is_success=True,
)
FAILED_DELETE_RESPONSE = HidePlanResponse(
    plan_id=uuid4(),
    is_success=False,
)


class HidePlanPresenterTests(TestCase):
    def setUp(self):
        self.presenter = HidePlanPresenter()

    def test_that_a_notification_is_shown_when_deletion_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_DELETE_RESPONSE)
        self.assertTrue(presentation.notifications)

    def test_that_no_notification_is_shown_when_deletion_was_a_failure(self):
        presentation = self.presenter.present(FAILED_DELETE_RESPONSE)
        self.assertFalse(presentation.notifications)
