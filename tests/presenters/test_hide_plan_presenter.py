from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.hide_plan import HidePlanResponse
from arbeitszeit_web.hide_plan import HidePlanPresenter
from tests.translator import FakeTranslator

from .notifier import NotifierTestImpl

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
        self.notifier = NotifierTestImpl()
        self.trans = FakeTranslator()
        self.presenter = HidePlanPresenter(notifier=self.notifier, trans=self.trans)

    def test_that_a_notification_is_shown_when_deletion_was_successful(self):
        self.presenter.present(SUCCESSFUL_DELETE_RESPONSE)
        self.assertTrue(self.notifier.infos)

    def test_that_no_notification_is_shown_when_deletion_was_a_failure(self):
        self.presenter.present(FAILED_DELETE_RESPONSE)
        self.assertFalse(self.notifier.infos)
