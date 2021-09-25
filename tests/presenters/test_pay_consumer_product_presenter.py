from unittest import TestCase

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.pay_consumer_product import PayConsumerProductPresenter


class PayConsumerProductPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = PayConsumerProductPresenter()

    def test_presenter_shows_correct_notification_when_payment_was_a_success(
        self,
    ) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=None)
        )
        self.assertIn("Produkt erfolgreich bezahlt.", view_model.notifications)

    def test_presenter_shows_correct_notification_when_plan_was_inactive(self) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_inactive)
        )
        self.assertIn(
            "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten.",
            view_model.notifications,
        )

    def test_presenter_shows_correct_notification_when_plan_was_not_found(self) -> None:
        view_model = self.presenter.present(
            PayConsumerProductResponse(rejection_reason=RejectionReason.plan_not_found)
        )
        self.assertIn(
            "Ein Plan mit der angegebene ID existiert nicht im System.",
            view_model.notifications,
        )
