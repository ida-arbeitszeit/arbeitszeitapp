from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import CreateCooperationResponse
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter

SUCCESSFUL_CREATE_RESPONSE = CreateCooperationResponse(
    rejection_reason=None, cooperation_id=uuid4()
)

REJECTED_RESPONSE_NAME_EXISTS = CreateCooperationResponse(
    rejection_reason=CreateCooperationResponse.RejectionReason.cooperation_with_name_exists,
    cooperation_id=None,
)

REJECTED_RESPONSE_COORDINATOR_NOT_FOUND = CreateCooperationResponse(
    rejection_reason=CreateCooperationResponse.RejectionReason.coordinator_not_found,
    cooperation_id=None,
)


class CreateCooperationPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = CreateCooperationPresenter()

    def test_no_notifications_are_returned_when_creation_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertFalse(presentation.notifications)

    def test_notification_returned_when_creation_was_rejected_because_coop_name_existed(
        self,
    ):
        presentation = self.presenter.present(REJECTED_RESPONSE_NAME_EXISTS)
        self.assertTrue(presentation.notifications)

    def test_notification_returned_when_creation_was_rejected_because_coordinator_not_found(
        self,
    ):
        presentation = self.presenter.present(REJECTED_RESPONSE_COORDINATOR_NOT_FOUND)
        self.assertTrue(presentation.notifications)
