from unittest import TestCase

from arbeitszeit.use_cases import RequestCooperationResponse
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

RejectionReason = RequestCooperationResponse.RejectionReason

SUCCESSFUL_COOPERATION_REQUEST = RequestCooperationResponse(rejection_reason=None)


class RequestCooperationPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
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
        self.assertEqual(
            presentation.notifications[0], self.translator.gettext("Plan not found.")
        )

    def test_correct_notification_when_rejected_because_coop_not_found(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(
                rejection_reason=RejectionReason.cooperation_not_found
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext("Cooperation not found."),
        )

    def test_correct_notification_when_rejected_because_plan_inactive(self):
        presentation = self.presenter.present(
            RequestCooperationResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertEqual(
            presentation.notifications[0], self.translator.gettext("Plan not active.")
        )

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
            self.translator.gettext(
                "Plan is already cooperating or requested a cooperation."
            ),
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
            self.translator.gettext(
                "Plan is already cooperating or requested a cooperation."
            ),
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
            self.translator.gettext("Public plans cannot cooperate."),
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
            self.translator.gettext(
                "Only the creator of a plan can request a cooperation."
            ),
        )
