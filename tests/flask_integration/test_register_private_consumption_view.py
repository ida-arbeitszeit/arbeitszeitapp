from decimal import Decimal
from uuid import uuid4

from tests.data_generators import PlanGenerator, TransactionGenerator

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.member = self.login_member()
        self.url = "/member/register_private_consumption"

    def test_get_returns_200_status(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_posting_with_invalid_form_data_results_in_400(self) -> None:
        response = self.client.post(
            self.url,
            data=dict(
                plan_id=uuid4(),
                amount="abc",
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_posting_with_valid_form_data_results_in_302(self) -> None:
        account = (
            self.database_gateway.get_accounts().owned_by_member(self.member).first()
        )
        assert account
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_received=Decimal(100)
        )
        plan = self.plan_generator.create_plan()
        response = self.client.post(
            self.url,
            data=dict(
                plan_id=plan,
                amount=2,
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_posting_with_nonexisting_plan_id_results_in_404(self) -> None:
        response = self.client.post(
            self.url,
            data=dict(
                plan_id=uuid4(),
                amount=2,
            ),
        )
        self.assertEqual(response.status_code, 404)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()
        self.url = "/member/register_private_consumption"

    def test_company_gets_redirected_when_trying_to_access_consumer_product_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
