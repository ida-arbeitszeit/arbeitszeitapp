from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import CreateCooperationResponse
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter

from .notifier import NotifierTestImpl

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
        self.notifier = NotifierTestImpl()
        self.presenter = CreateCooperationPresenter(user_notifier=self.notifier)

    def test_notification_returned_when_creation_was_successful(self):
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertTrue(self._get_info_notifications())

    def test_correct_notification_returned_when_creation_was_successful(self):
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertIn(
            "Kooperation erfolgreich erstellt.", self._get_info_notifications()
        )

    def test_notification_returned_when_creation_was_rejected_because_coop_name_existed(
        self,
    ):
        self.presenter.present(REJECTED_RESPONSE_NAME_EXISTS)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_creation_was_rejected_because_coop_name_existed(
        self,
    ):
        self.presenter.present(REJECTED_RESPONSE_NAME_EXISTS)
        self.assertIn(
            "Es existiert bereits eine Kooperation mit diesem Namen.",
            self._get_warning_notifications(),
        )

    def test_notification_returned_when_creation_was_rejected_because_coordinator_not_found(
        self,
    ):
        self.presenter.present(REJECTED_RESPONSE_COORDINATOR_NOT_FOUND)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_creation_was_rejected_because_coordinator_not_found(
        self,
    ):
        self.presenter.present(REJECTED_RESPONSE_COORDINATOR_NOT_FOUND)
        self.assertIn(
            "Interner Fehler: Koordinator nicht gefunden.",
            self._get_warning_notifications(),
        )

    def _get_info_notifications(self) -> List[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> List[str]:
        return self.notifier.warnings
