from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.create_offer import CreateOfferResponse, RejectionReason
from arbeitszeit_web.create_offer import CreateOfferPresenter

SUCCESSFUL_CREATION_RESPONSE = CreateOfferResponse(
    id=uuid4(), name="testname", description="testdescription", rejection_reason=None
)
FAILED_CREATION_RESPONSE = CreateOfferResponse(
    id=None, name=None, description=None, rejection_reason=RejectionReason.plan_inactive
)


class CreateOfferPresenterTests(TestCase):
    def setUp(self):
        self.presenter = CreateOfferPresenter()

    def test_that_a_notification_is_shown_when_creation_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_CREATION_RESPONSE)
        self.assertTrue(presentation.notifications)

    def test_that_a_notification_is_shown_when_creation_was_a_failure(self):
        presentation = self.presenter.present(FAILED_CREATION_RESPONSE)
        self.assertTrue(presentation.notifications)

    def test_that_correct_notification_is_shown_when_creation_was_successful(self):
        presentation = self.presenter.present(SUCCESSFUL_CREATION_RESPONSE)
        self.assertTrue(
            presentation.notifications[0]
            == "Dein Angebot wurde erfolgreich in unserem Marketplace veröffentlicht."
        )

    def test_that_correct_notification_is_shown_when_creation_was_a_failure(self):
        presentation = self.presenter.present(FAILED_CREATION_RESPONSE)
        self.assertTrue(
            presentation.notifications[0]
            == "Angebot wurde nicht veröffentlicht. Der Plan ist nicht aktiv."
        )
