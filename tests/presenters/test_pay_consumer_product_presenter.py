from unittest import TestCase

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.pay_consumer_product import PayConsumerProductPresenter
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl


class PayConsumerProductPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(PayConsumerProductPresenter)

    def test_presenter_shows_correct_notification_when_payment_was_a_success(
        self,
    ) -> None:
        self.presenter.present(PayConsumerProductResponse(rejection_reason=None))
        self.assertIn(
            self.translator.gettext("Product successfully paid."), self.notifier.infos
        )

    def test_presenter_shows_correct_notification_when_plan_was_inactive(self) -> None:
        self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertIn(
            self.translator.gettext(
                "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
            ),
            self.notifier.warnings,
        )

    def test_presenter_shows_correct_notification_when_plan_was_not_found(self) -> None:
        self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertIn(
            self.translator.gettext(
                "There is no plan with the specified ID in the database."
            ),
            self.notifier.warnings,
        )

    def test_presenter_returns_404_status_code_when_plan_was_not_found(self) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertEqual(view_model.status_code, 404)

    def test_presenter_returns_200_status_code_when_payment_was_accepted(self) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=None)
        )
        self.assertEqual(view_model.status_code, 200)

    def test_presenter_returns_410_status_code_when_plan_is_inactive(self) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertEqual(view_model.status_code, 410)
