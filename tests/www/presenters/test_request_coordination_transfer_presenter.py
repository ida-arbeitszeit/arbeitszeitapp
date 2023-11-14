from uuid import uuid4

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.www.presenters.request_coordination_transfer_presenter import (
    RequestCoordinationTransferPresenter,
)
from tests.www.base_test_case import BaseTestCase


class RequestCoordinationTransferPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCoordinationTransferPresenter)

    def test_do_not_show_as_error_if_request_was_successful(self):
        presentation = self.presenter.present(self.get_successful_request())
        self.assertFalse(presentation.is_error)

    def test_show_correct_notificiation_if_request_was_successful(self):
        presentation = self.presenter.present(self.get_successful_request())
        expected = self.translator.gettext("Request has been sent.")
        self.assertEqual(presentation.notifications[0], expected)

    def test_show_as_error_if_request_was_rejected(self):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertTrue(presentation.is_error)

    def test_correct_notification_when_rejected_because_candidate_is_not_a_company(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext("The candidate is not a company."),
        )

    def test_correct_notification_when_rejected_because_requesting_tenure_not_found(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.requesting_tenure_not_found
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext("Requesting coordination tenure not found."),
        )

    def test_correct_notification_when_rejected_because_candidate_is_current_coordinator(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_current_coordinator
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext("The candidate is already the coordinator."),
        )

    def test_correct_notification_when_rejected_because_requesting_tenure_is_not_current_tenure(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.requesting_tenure_is_not_current_tenure
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext(
                "The requesting coordination tenure is not the current tenure."
            ),
        )

    def test_correct_notification_when_rejected_because_requesting_tenure_has_pending_transfer_request(
        self,
    ):
        presentation = self.presenter.present(
            self.get_rejected_request(
                rejection_reason=UseCase.Response.RejectionReason.requesting_tenure_has_pending_transfer_request
            )
        )
        self.assertEqual(
            presentation.notifications[0],
            self.translator.gettext(
                "The requesting coordination tenure has a pending transfer request."
            ),
        )

    def get_rejected_request(
        self, rejection_reason: UseCase.Response.RejectionReason
    ) -> UseCase.Response:
        return UseCase.Response(
            rejection_reason=rejection_reason,
            transfer_request=None,
        )

    def get_successful_request(self) -> UseCase.Response:
        return UseCase.Response(
            rejection_reason=None,
            transfer_request=uuid4(),
        )
