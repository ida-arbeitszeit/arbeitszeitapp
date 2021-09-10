from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.query_products import ProductQueryResponse, QueriedProduct
from arbeitszeit_web.query_products import QueryProductsPresenter


class QueryProductsPresenterTests(TestCase):
    def setUp(self):
        self.presenter = QueryProductsPresenter()

    def test_presenting_empty_response_leads_to_not_showing_results(self):
        use_case_response = ProductQueryResponse(results=[])
        presentation = self.presenter.present(use_case_response)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        use_case_response = ProductQueryResponse(
            results=[
                QueriedProduct(
                    offer_id=uuid4(),
                    seller_name="Seller name",
                    seller_email="seller@cp.org",
                    plan_id=uuid4(),
                    product_name="Bread",
                    product_description="For eating",
                    price_per_unit=Decimal(0.001),
                    is_public_service=True,
                )
            ]
        )
        presentation = self.presenter.present(use_case_response)
        self.assertTrue(presentation.show_results)
