from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.accept_coordination_transfer_presenter import (
    AcceptCoordinationTransferPresenter,
)
from tests.www.base_test_case import BaseTestCase

rejection_reason = AcceptCoordinationTransferUseCase.Response.RejectionReason


class AcceptCoordinationTransferPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(AcceptCoordinationTransferPresenter)

    def test_that_no_redirect_url_is_returned_if_transfer_request_was_not_found(
        self,
    ) -> None:
        response = self.presenter.present(
            self.uc_response(
                rejection_reason=rejection_reason.transfer_request_not_found
            )
        )
        self.assertIsNone(response.redirect_url)

    def test_that_status_code_is_404_if_transfer_request_was_not_found(self) -> None:
        response = self.presenter.present(
            self.uc_response(
                rejection_reason=rejection_reason.transfer_request_not_found
            )
        )
        self.assertEqual(404, response.status_code)

    def test_that_correct_warning_is_displayed_if_transfer_request_was_not_found(
        self,
    ) -> None:
        self.presenter.present(
            self.uc_response(
                rejection_reason=rejection_reason.transfer_request_not_found
            )
        )
        expected = self.translator.gettext("Transfer request not found.")
        self.assertEqual(self.notifier.warnings[0], expected)

    def test_that_no_redirect_url_is_returned_if_transfer_request_was_closed(
        self,
    ) -> None:
        response = self.presenter.present(
            self.uc_response(rejection_reason=rejection_reason.transfer_request_closed)
        )
        self.assertIsNone(response.redirect_url)

    def test_that_status_code_is_409_if_transfer_request_was_closed(self) -> None:
        response = self.presenter.present(
            self.uc_response(rejection_reason=rejection_reason.transfer_request_closed)
        )
        self.assertEqual(409, response.status_code)

    def test_that_correct_warning_is_displayed_if_transfer_request_was_closed(
        self,
    ) -> None:
        self.presenter.present(
            self.uc_response(rejection_reason=rejection_reason.transfer_request_closed)
        )
        expected = self.translator.gettext("This request is not valid anymore.")
        self.assertEqual(self.notifier.warnings[0], expected)

    def test_that_a_redirect_url_is_returned_if_transfer_request_was_accepted(
        self,
    ) -> None:
        response = self.presenter.present(self.uc_response(cooperation_id=uuid4()))
        self.assertIsNotNone(response.redirect_url)

    def test_that_status_code_is_304_if_transfer_request_was_accepted(self) -> None:
        response = self.presenter.present(self.uc_response(cooperation_id=uuid4()))
        self.assertEqual(304, response.status_code)

    def test_that_correct_info_is_displayed_if_transfer_request_was_accepted(
        self,
    ) -> None:
        self.presenter.present(self.uc_response(cooperation_id=uuid4()))
        expected = self.translator.gettext(
            "Successfully accepted the request. You are now coordinator of the cooperation."
        )
        self.assertEqual(self.notifier.infos[0], expected)

    def test_that_redirect_url_is_correct_if_transfer_request_was_accepted(
        self,
    ) -> None:
        cooperation_id = uuid4()
        response = self.presenter.present(
            self.uc_response(cooperation_id=cooperation_id)
        )
        expected_url = self.url_index.get_coop_summary_url(
            coop_id=cooperation_id, user_role=UserRole.company
        )
        self.assertEqual(response.redirect_url, expected_url)

    def uc_response(
        self,
        rejection_reason: Optional[rejection_reason] = None,
        cooperation_id: Optional[UUID] = None,
    ) -> AcceptCoordinationTransferUseCase.Response:
        return AcceptCoordinationTransferUseCase.Response(
            rejection_reason=rejection_reason, cooperation_id=cooperation_id
        )
