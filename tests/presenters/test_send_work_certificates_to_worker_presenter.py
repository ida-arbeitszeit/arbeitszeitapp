from unittest import TestCase

from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorkerResponse,
)
from arbeitszeit_web.controllers.send_work_certificates_to_worker_controller import (
    ControllerRejection,
)
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)

from ..translator import FakeTranslator
from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl

SUCCESS_USE_CASE_RESPONSE = SendWorkCertificatesToWorkerResponse(rejection_reason=None)

REJECTED_USE_CASE_RESPONSE = SendWorkCertificatesToWorkerResponse(
    rejection_reason=SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
)

REJECTED_CONTROLLER_RES_INVALID_INPUT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.invalid_input
)

REJECTED_CONTROLLER_RES_NEGATIVE_AMOUNT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.negative_amount
)


class PresentUseCaseResponseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.presenter = self.injector.get(SendWorkCertificatesToWorkerPresenter)

    def test_presenter_renders_warning_if_use_case_response_is_rejected(self):
        self.presenter.present_use_case_response(REJECTED_USE_CASE_RESPONSE)
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)

    def test_presenter_returns_status_404_if_use_case_response_is_rejected(self):
        code = self.presenter.present_use_case_response(REJECTED_USE_CASE_RESPONSE)
        self.assertEqual(code, 404)

    def test_presenter_renders_info_if_use_case_response_is_successfull(self):
        self.presenter.present_use_case_response(SUCCESS_USE_CASE_RESPONSE)
        self.assertTrue(self.notifier.infos)
        self.assertFalse(self.notifier.warnings)

    def test_presenter_returns_status_200_if_use_case_response_is_successfull(self):
        code = self.presenter.present_use_case_response(SUCCESS_USE_CASE_RESPONSE)
        self.assertEqual(code, 200)


class PresentControllerResponseTests(TestCase):
    def setUp(self) -> None:
        self.translator = FakeTranslator()
        self.notifier = NotifierTestImpl()
        self.presenter = SendWorkCertificatesToWorkerPresenter(
            notifier=self.notifier, translator=self.translator
        )

    def test_presenter_renders_correct_warning_if_controller_rejects_invalid_input(
        self,
    ):
        self.presenter.present_controller_warnings(
            REJECTED_CONTROLLER_RES_INVALID_INPUT
        )
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)
        self.assertIn(self.translator.gettext("Invalid input"), self.notifier.warnings)

    def test_presenter_renders_correct_warning_if_controller_rejects_negative_amount(
        self,
    ):
        self.presenter.present_controller_warnings(
            REJECTED_CONTROLLER_RES_NEGATIVE_AMOUNT
        )
        self.assertTrue(self.notifier.warnings)
        self.assertFalse(self.notifier.infos)
        self.assertIn(
            self.translator.gettext("A negative amount is not allowed."),
            self.notifier.warnings,
        )
