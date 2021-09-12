from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.query_products import ProductQueryResponse, QueriedProduct
from arbeitszeit_web.query_products import QueryProductsPresenter

RESPONSE_WITHOUT_RESULTS = ProductQueryResponse(results=[])
RESPONSE_WITH_ONE_RESULT = ProductQueryResponse(
    results=[
        QueriedProduct(
            offer_id=uuid4(),
            seller_name="Seller name",
            seller_email="seller@cp.org",
            plan_id=uuid4(),
            product_name="Bread",
            product_description="For eating",
            price_per_unit=Decimal(0.001),
        )
    ]
)


class QueryProductsPresenterTests(TestCase):
    def setUp(self):
        self.presenter = QueryProductsPresenter()

    def test_presenting_empty_response_leads_to_not_showing_results(self):
        presentation = self.presenter.present(RESPONSE_WITHOUT_RESULTS)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertTrue(presentation.show_results)

    def test_show_notification_when_no_results_are_found(self):
        presentation = self.presenter.present(RESPONSE_WITHOUT_RESULTS)
        self.assertTrue(presentation.notifications)

    def test_dont_show_notifications_when_results_are_found(self):
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertFalse(presentation.notifications)
