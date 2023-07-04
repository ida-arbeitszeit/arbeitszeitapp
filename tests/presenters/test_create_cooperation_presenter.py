from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.create_cooperation import CreateCooperationResponse
from arbeitszeit_web.www.presenters.create_cooperation_presenter import (
    CreateCooperationPresenter,
)
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
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
        self.injector = get_dependency_injector()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(CreateCooperationPresenter)

    def test_notification_returned_when_creation_was_successful(self):
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertTrue(self._get_info_notifications())

    def test_correct_notification_returned_when_creation_was_successful(self):
        self.presenter.present(SUCCESSFUL_CREATE_RESPONSE)
        self.assertIn(
            self.translator.gettext("Successfully created cooperation."),
            self._get_info_notifications(),
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
            self.translator.gettext(
                "There is already a cooperation with the same name."
            ),
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
            self.translator.gettext("Internal error: Coordinator not found."),
            self._get_warning_notifications(),
        )

    def _get_info_notifications(self) -> List[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> List[str]:
        return self.notifier.warnings
