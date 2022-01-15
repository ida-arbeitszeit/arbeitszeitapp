from unittest import TestCase

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.pay_consumer_product import PayConsumerProductPresenter

from .notifier import NotifierTestImpl


class PayConsumerProductPresenterTests(TestCase):
    def setUp(self) -> None:
        self.notifier = NotifierTestImpl()
        self.presenter = PayConsumerProductPresenter(user_notifier=self.notifier)

    def test_presenter_shows_correct_notification_when_payment_was_a_success(
        self,
    ) -> None:
        self.presenter.present(PayConsumerProductResponse(rejection_reason=None))
        self.assertIn("Produkt erfolgreich bezahlt.", self.notifier.infos)

    def test_presenter_shows_correct_notification_when_plan_was_inactive(self) -> None:
        self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertIn(
            "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten.",
            self.notifier.warnings,
        )

    def test_presenter_shows_correct_notification_when_plan_was_not_found(self) -> None:
        self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertIn(
            "Ein Plan mit der angegebene ID existiert nicht im System.",
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
