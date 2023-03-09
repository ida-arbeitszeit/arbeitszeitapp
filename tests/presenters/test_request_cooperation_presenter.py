from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases.request_cooperation import RequestCooperationResponse
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter
from tests.email import FakeEmailSender
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

RejectionReason = RequestCooperationResponse.RejectionReason


class RequestCooperationPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RequestCooperationPresenter)
        self.mail_service = self.injector.get(FakeEmailSender)

    def test_do_not_show_as_error_if_request_was_successful(self):
        presentation = self.presenter.present(self.get_successful_request())
        self.assertFalse(presentation.is_error)

    def test_show_correct_notificiation_if_request_was_successful(self):
        presentation = self.presenter.present(self.get_successful_request())
        expected = self.translator.gettext("Request has been sent.")
        self.assertEqual(presentation.notifications[0], expected)

    def test_mail_gets_sent_if_request_was_successful(self):
        self.presenter.present(self.get_successful_request())
        self.assertTrue(self.mail_service.sent_mails)

    def test_mail_gets_sent_to_coordinator_if_request_was_successful(self):
        recipient = "company@comp.any"
        self.presenter.present(self.get_successful_request(coordinator_mail=recipient))
        self.assertEqual(self.mail_service.sent_mails[0].recipients, [recipient])

    def test_mail_gets_sent_and_subject_and_html_body_are_not_empty(self):
        self.presenter.present(self.get_successful_request())
        self.assertTrue(self.mail_service.sent_mails[0].subject)
        self.assertTrue(self.mail_service.sent_mails[0].html)

    def test_mail_html_body_has_name_of_coordinator_safely_escaped(self):
        coordinator_name = '<a href="dangerous site">coordinator</a>'
        self.presenter.present(
            self.get_successful_request(coordinator_name=coordinator_name)
        )
        self.assertIn(
            "&lt;a href=&quot;dangerous site&quot;&gt;coordinator&lt;/a&gt;",
            self.mail_service.sent_mails[0].html,
        )

    def test_show_as_error_if_request_was_rejected(self):
        presentation = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertTrue(presentation.is_error)

    def test_correct_notification_when_rejected_because_plan_not_found(self):
        presentation = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertEqual(
            presentation.notifications[0], self.translator.gettext("Plan not found.")
        )

    def test_correct_notification_when_rejected_because_coop_not_found(self):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=RejectionReason.cooperation_not_found
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext("Cooperation not found."),
        )

    def test_correct_notification_when_rejected_because_plan_inactive(self):
        presentation = self.presenter.present(
            self.get_rejected_request(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertEqual(
            presentation.notifications[0], self.translator.gettext("Plan not active.")
        )

    def test_correct_notification_when_rejected_because_plan_has_cooperation(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
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
            self.get_rejected_request(
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
            self.get_rejected_request(
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
            self.get_rejected_request(
                rejection_reason=RejectionReason.requester_is_not_planner
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext(
                "Only the creator of a plan can request a cooperation."
            ),
        )

    def get_rejected_request(
        self, rejection_reason: RequestCooperationResponse.RejectionReason
    ) -> RequestCooperationResponse:
        return RequestCooperationResponse(
            coordinator_name=None,
            coordinator_email=None,
            rejection_reason=rejection_reason,
        )

    def get_successful_request(
        self,
        coordinator_mail: Optional[str] = None,
        coordinator_name: Optional[str] = None,
    ) -> RequestCooperationResponse:
        if coordinator_mail is None:
            coordinator_mail = "company@comp.any"
        if coordinator_name is None:
            coordinator_name = "company xy"
        return RequestCooperationResponse(
            coordinator_name=coordinator_name,
            coordinator_email=coordinator_mail,
            rejection_reason=None,
        )
