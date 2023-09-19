from arbeitszeit.use_cases.register_hours_worked import RegisterHoursWorkedResponse
from arbeitszeit_web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
)
from arbeitszeit_web.www.presenters.register_hours_worked_presenter import (
    RegisterHoursWorkedPresenter,
)
from tests.www.base_test_case import BaseTestCase

SUCCESS_USE_CASE_RESPONSE = RegisterHoursWorkedResponse(rejection_reason=None)

REJECTED_USE_CASE_RESPONSE = RegisterHoursWorkedResponse(
    rejection_reason=RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
)

REJECTED_CONTROLLER_RES_INVALID_INPUT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.invalid_input
)

REJECTED_CONTROLLER_RES_NEGATIVE_AMOUNT = ControllerRejection(
    reason=ControllerRejection.RejectionReason.negative_amount
)


class PresentUseCaseResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterHoursWorkedPresenter)

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

    def test_that_the_user_is_notified_about_success(self) -> None:
        self.presenter.present_use_case_response(SUCCESS_USE_CASE_RESPONSE)
        assert (
            self.translator.gettext("Labour hours successfully registered")
            in self.notifier.infos
        )


class PresentControllerResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = RegisterHoursWorkedPresenter(
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
