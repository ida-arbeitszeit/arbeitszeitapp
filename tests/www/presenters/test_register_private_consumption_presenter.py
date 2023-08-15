from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionResponse,
    RejectionReason,
)
from arbeitszeit_web.www.presenters.register_private_consumption_presenter import (
    RegisterPrivateConsumptionPresenter,
)
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

from .notifier import NotifierTestImpl


class RegisterPrivateConsumptionPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegisterPrivateConsumptionPresenter)

    def test_presenter_shows_correct_notification_when_registration_was_a_success(
        self,
    ) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=None)
        )
        self.assertIn(
            self.translator.gettext("Consumption successfully registered."),
            self.notifier.infos,
        )

    def test_presenter_shows_correct_notification_when_plan_was_inactive(self) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_inactive
            )
        )
        self.assertIn(
            self.translator.gettext(
                "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
            ),
            self.notifier.warnings,
        )

    def test_presenter_shows_correct_notification_when_plan_was_not_found(self) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_not_found
            )
        )
        self.assertIn(
            self.translator.gettext(
                "There is no plan with the specified ID in the database."
            ),
            self.notifier.warnings,
        )

    def test_presenter_shows_correct_notification_when_member_has_insufficient_balance(
        self,
    ) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )
        )
        self.assertIn(
            self.translator.gettext("You do not have enough work certificates."),
            self.notifier.warnings,
        )

    def test_presenter_returns_404_status_code_when_plan_was_not_found(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_not_found
            )
        )
        self.assertEqual(view_model.status_code, 404)

    def test_presenter_returns_200_status_code_when_registration_was_accepted(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=None)
        )
        self.assertEqual(view_model.status_code, 200)

    def test_presenter_returns_410_status_code_when_plan_is_inactive(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_inactive
            )
        )
        self.assertEqual(view_model.status_code, 410)

    def test_presenter_returns_406_status_code_when_member_has_insufficient_balance(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.insufficient_balance
            )
        )
        self.assertEqual(view_model.status_code, 406)

    def test_for_proper_error_message_if_user_does_not_exist(
        self,
    ) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.consumer_does_not_exist
            )
        )
        self.assertIn(
            self.translator.gettext(
                "Failed to register private consumption. Are you logged in as a member?"
            ),
            self.notifier.warnings,
        )

    def test_presenter_returns_404_status_code_when_consumer_does_not_exist(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.consumer_does_not_exist
            )
        )
        self.assertEqual(view_model.status_code, 404)
