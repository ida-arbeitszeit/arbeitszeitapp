from unittest import TestCase

from arbeitszeit.use_cases import RequestCooperationResponse
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter

from .dependency_injection import get_dependency_injector

RejectionReason = RequestCooperationResponse.RejectionReason

SUCCESSFUL_COOPERATION_REQUEST = RequestCooperationResponse(rejection_reason=None)


class RequestCooperationPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(RequestCooperationPresenter)

    def test_do_not_show_as_error_if_request_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_COOPERATION_REQUEST)
        self.assertFalse(presentation.is_error)

    def test_show_as_error_if_request_was_rejected(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertTrue(presentation.is_error)

    def test_correct_notification_when_rejected_because_plan_not_found(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertEqual(presentation.notifications[0], "Plan nicht gefunden.")

    def test_correct_notification_when_rejected_because_coop_not_found(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.cooperation_not_found
            )
        )
        self.assertEqual(presentation.notifications[0], "Kooperation nicht gefunden.")

    def test_correct_notification_when_rejected_because_plan_inactive(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertEqual(presentation.notifications[0], "Plan nicht aktiv.")

    def test_correct_notification_when_rejected_because_plan_has_cooperation(
        self,
    ):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.plan_has_cooperation
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            "Plan kooperiert bereits oder hat Kooperation angefragt.",
        )

    def test_correct_notification_when_rejected_because_plan_is_requesting_cooperation(
        self,
    ):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.plan_is_already_requesting_cooperation
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            "Plan kooperiert bereits oder hat Kooperation angefragt.",
        )

    def test_correct_notification_when_rejected_because_plan_is_public_service(
        self,
    ):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.plan_is_public_service
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            "Öffentliche Pläne können nicht kooperieren.",
        )

    def test_correct_notification_when_rejected_because_requester_not_planner(
        self,
    ):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.requester_is_not_planner
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            "Nur der Ersteller des Plans kann Kooperation anfragen.",
        )
