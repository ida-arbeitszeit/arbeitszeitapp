from typing import Optional

from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumptionResponse,
)
from arbeitszeit_web.www.presenters.register_productive_consumption_presenter import (
    RegisterProductiveConsumptionPresenter,
)
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl

reasons = RegisterProductiveConsumptionResponse.RejectionReason


class RegisterProductiveConsumptionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.trans = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(RegisterProductiveConsumptionPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_show_confirmation_when_registration_was_successful(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=None,
            )
        )
        self.assertIn(
            self.trans.gettext("Successfully registrated."), self.notifier.infos
        )

    def test_missing_plan_show_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.plan_not_found,
            )
        )
        self.assertIn(
            self.trans.gettext("Plan does not exist."), self.notifier.warnings
        )

    def test_invalid_purpose_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.invalid_purpose,
            )
        )
        self.assertIn(
            self.trans.gettext("The specified purpose is invalid."),
            self.notifier.warnings,
        )

    def test_inactive_plan_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.plan_is_not_active,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "The specified plan has expired. Please contact the provider to obtain a current plan ID."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_consume_public_service_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.cannot_consume_public_service,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "Registration failed. Companies cannot acquire public products."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_consume_own_product_shows_correct_notification(self) -> None:
        self.presenter.present(
            RegisterProductiveConsumptionResponse(
                rejection_reason=reasons.consumer_is_planner,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "Registration failed. Companies cannot acquire their own products."
            ),
            self.notifier.warnings,
        )

    def test_that_redirect_url_is_not_set_when_registration_got_rejected(self) -> None:
        response = self.create_failed_response()
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.redirect_url)

    def test_that_redirect_url_is_set_when_response_is_success(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertIsNotNone(view_model.redirect_url)

    def test_that_user_gets_redirected_to_registration_form(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_register_productive_consumption_url(),
        )

    def create_success_response(self) -> RegisterProductiveConsumptionResponse:
        return RegisterProductiveConsumptionResponse(rejection_reason=None)

    def create_failed_response(
        self,
        reason: Optional[RegisterProductiveConsumptionResponse.RejectionReason] = None,
    ) -> RegisterProductiveConsumptionResponse:
        if reason is None:
            reason = reasons.consumer_is_planner
        return RegisterProductiveConsumptionResponse(rejection_reason=reason)
