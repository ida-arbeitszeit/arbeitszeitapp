from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionResponse
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl

reasons = PayMeansOfProductionResponse.RejectionReason


class PayMeansOfProductionTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.trans = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(PayMeansOfProductionPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_show_confirmation_when_payment_was_successful(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=None,
            )
        )
        self.assertIn(self.trans.gettext("Successfully paid."), self.notifier.infos)

    def test_missing_plan_show_correct_notification(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=reasons.plan_not_found,
            )
        )
        self.assertIn(
            self.trans.gettext("Plan does not exist."), self.notifier.warnings
        )

    def test_invalid_purpose_shows_correct_notification(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=reasons.invalid_purpose,
            )
        )
        self.assertIn(
            self.trans.gettext("The specified purpose is invalid."),
            self.notifier.warnings,
        )

    def test_inactive_plan_shows_correct_notification(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=reasons.plan_is_not_active,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "The specified plan has expired. Please contact the provider to obtain a current plan ID."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_pay_public_service_shows_correct_notification(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=reasons.cannot_buy_public_service,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "Payment failed. Companies cannot acquire public products."
            ),
            self.notifier.warnings,
        )

    def test_trying_to_pay_for_own_product_shows_correct_notification(self) -> None:
        self.presenter.present(
            PayMeansOfProductionResponse(
                rejection_reason=reasons.buyer_is_planner,
            )
        )
        self.assertIn(
            self.trans.gettext(
                "Payment failed. Companies cannot acquire their own products."
            ),
            self.notifier.warnings,
        )

    def test_that_redirect_url_is_not_set_when_payment_got_rejected(self) -> None:
        response = self.create_failed_response()
        view_model = self.presenter.present(response)
        self.assertIsNone(view_model.redirect_url)

    def test_that_redirect_url_is_set_when_response_is_success(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertIsNotNone(view_model.redirect_url)

    def test_that_user_gets_redirected_to_pay_means_form(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_pay_means_of_production_url(),
        )

    def create_success_response(self) -> PayMeansOfProductionResponse:
        return PayMeansOfProductionResponse(rejection_reason=None)

    def create_failed_response(
        self, reason: Optional[PayMeansOfProductionResponse.RejectionReason] = None
    ) -> PayMeansOfProductionResponse:
        if reason is None:
            reason = reasons.buyer_is_planner
        return PayMeansOfProductionResponse(rejection_reason=reason)
