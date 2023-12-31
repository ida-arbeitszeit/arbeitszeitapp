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

    def test_no_warning_gets_issued_if_transfer_request_was_successful(self):
        self.presenter.present_use_case_response(self.get_successful_transfer_request())
        self.assertFalse(self.notifier.warnings)

    def test_one_info_notification_gets_issued_if_transfer_request_was_successful(self):
        self.presenter.present_use_case_response(self.get_successful_transfer_request())
        self.assertEqual(len(self.notifier.infos), 1)

    def test_show_correct_notificiation_if_transfer_request_was_successful(self):
        self.presenter.present_use_case_response(self.get_successful_transfer_request())
        expected = self.translator.gettext("Request has been sent.")
        self.assertEqual(self.notifier.infos[0], expected)

    def test_correct_status_code_if_transfer_request_was_successful(self):
        response = self.presenter.present_use_case_response(
            self.get_successful_transfer_request()
        )
        self.assertEqual(response.status_code, 200)

    def test_no_info_notification_gets_issued_if_request_was_rejected(self):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertFalse(self.notifier.infos)

    def test_one_warning_gets_issued_if_request_was_rejected(self):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertEqual(len(self.notifier.warnings), 1)

    def test_correct_notification_when_rejected_because_candidate_is_not_a_company(
        self,
    ):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertEqual(
            self.notifier.warnings[0],
            self.translator.gettext("The candidate is not a company."),
        )

    def test_correct_status_code_when_rejected_because_candidate_is_not_a_company(
        self,
    ):
        response = self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_not_a_company
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_correct_notification_when_rejected_because_cooperation_was_not_found(self):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.cooperation_not_found
            )
        )
        self.assertEqual(
            self.notifier.warnings[0],
            self.translator.gettext("Cooperation not found."),
        )

    def test_correct_status_code_when_rejected_because_cooperation_was_not_found(
        self,
    ):
        response = self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.cooperation_not_found
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_correct_notification_when_rejected_because_requester_is_not_coordinator(
        self,
    ):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.requester_is_not_coordinator
            )
        )
        self.assertEqual(
            self.notifier.warnings[0],
            self.translator.gettext("You are not the coordinator."),
        )

    def test_correct_status_code_when_rejected_because_requester_is_not_coordinator(
        self,
    ):
        response = self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.requester_is_not_coordinator
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_correct_notification_when_rejected_because_candidate_is_current_coordinator(
        self,
    ):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_current_coordinator
            )
        )
        self.assertEqual(
            self.notifier.warnings[0],
            self.translator.gettext("The candidate is already the coordinator."),
        )

    def test_correct_status_code_when_rejected_because_candidate_is_current_coordinator(
        self,
    ):
        response = self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.candidate_is_current_coordinator
            )
        )
        self.assertEqual(response.status_code, 409)

    def test_correct_notification_when_rejected_because_coordination_has_pending_transfer_request(
        self,
    ):
        self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.coordination_tenure_has_pending_transfer_request
            )
        )
        self.assertEqual(
            self.notifier.warnings[0],
            self.translator.gettext(
                "Request has not been sent. You have a pending transfer request."
            ),
        )

    def test_correct_status_code_when_rejected_because_coordination_has_pending_transfer_request(
        self,
    ):
        response = self.presenter.present_use_case_response(
            self.get_rejected_transfer_request(
                rejection_reason=UseCase.Response.RejectionReason.coordination_tenure_has_pending_transfer_request
            )
        )
        self.assertEqual(response.status_code, 409)

    def get_rejected_transfer_request(
        self, rejection_reason: UseCase.Response.RejectionReason
    ) -> UseCase.Response:
        return UseCase.Response(
            rejection_reason=rejection_reason,
            transfer_request=None,
        )

    def get_successful_transfer_request(self) -> UseCase.Response:
        return UseCase.Response(rejection_reason=None, transfer_request=uuid4())


class NavbarItemsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RequestCoordinationTransferPresenter)

    def test_two_navbar_items_are_shown(self) -> None:
        navbar_items = self.presenter.create_navbar_items(uuid4())
        self.assertTrue(len(navbar_items) == 2)

    def test_first_navbar_item_has_correct_text(self) -> None:
        navbar_items = self.presenter.create_navbar_items(uuid4())
        self.assertEqual(navbar_items[0].text, self.translator.gettext("Cooperation"))

    def test_first_navbar_item_has_link_to_cooperation(self) -> None:
        cooperation_id = uuid4()
        navbar_items = self.presenter.create_navbar_items(cooperation_id)
        self.assertEqual(
            navbar_items[0].url,
            self.url_index.get_coop_summary_url(
                coop_id=cooperation_id, user_role=self.session.get_user_role()
            ),
        )

    def test_second_navbar_item_has_correct_text(self) -> None:
        navbar_items = self.presenter.create_navbar_items(uuid4())
        self.assertEqual(
            navbar_items[1].text,
            self.translator.gettext("Request Coordination Transfer"),
        )

    def test_second_navbar_item_has_no_link(self) -> None:
        navbar_items = self.presenter.create_navbar_items(uuid4())
        self.assertIsNone(navbar_items[1].url)
