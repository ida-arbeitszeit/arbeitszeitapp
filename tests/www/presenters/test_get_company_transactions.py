from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from dateutil import tz

from arbeitszeit.records import AccountTypes
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactionsResponse,
    TransactionInfo,
)
from arbeitszeit_web.www.presenters.get_company_transactions_presenter import (
    GetCompanyTransactionsPresenter,
)
from tests.www.base_test_case import BaseTestCase


class CompanyTransactionsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCompanyTransactionsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self) -> None:
        response = self.create_use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_show_details_of_one_transaction_when_one_transaction_took_place(
        self,
    ) -> None:
        expected_transaction = self._get_single_transaction_info()
        response = self.create_use_case_response(transactions=[expected_transaction])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)

    def test_that_correct_string_is_shown_for_each_transaction_type(self) -> None:
        transaction_types = [
            TransactionTypes.credit_for_fixed_means,
            TransactionTypes.credit_for_liquid_means,
            TransactionTypes.credit_for_wages,
            TransactionTypes.consumption_of_fixed_means,
            TransactionTypes.consumption_of_liquid_means,
            TransactionTypes.payment_of_wages,
            TransactionTypes.expected_sales,
            TransactionTypes.sale_of_consumer_product,
            TransactionTypes.sale_of_fixed_means,
            TransactionTypes.sale_of_liquid_means,
        ]
        for transaction_type in transaction_types:
            with self.subTest():
                expected_transaction = self._get_single_transaction_info(
                    transaction_type=transaction_type
                )
                response = self.create_use_case_response(
                    transactions=[expected_transaction]
                )
                view_model = self.presenter.present(response)
                presented_transaction = view_model.transactions[0]
                self.assertEqual(
                    presented_transaction.transaction_type,
                    self._get_transaction_name(transaction_type),
                )

    def test_that_transaction_date_is_formatted_as_string(self) -> None:
        expected_transaction = self._get_single_transaction_info()
        response = self.create_use_case_response(transactions=[expected_transaction])
        view_model = self.presenter.present(response)
        presented_transaction = view_model.transactions[0]
        self.assertIsInstance(presented_transaction.date, str)

    def test_that_transaction_date_is_formatted_correctly(self) -> None:
        expected_time = datetime(1998, 12, 1, 22, 5, tzinfo=tz.gettz("Europe/Berlin"))
        expected_transaction = self._get_single_transaction_info(date=expected_time)
        response = self.create_use_case_response(transactions=[expected_transaction])
        view_model = self.presenter.present(response)
        presented_transaction = view_model.transactions[0]
        self.assertEqual(presented_transaction.date, "01.12.1998 22:05")

    def test_that_transaction_volume_is_shown_as_correct_decimal(self) -> None:
        expected_transaction_volume = Decimal(10)
        expected_transaction = self._get_single_transaction_info(
            transaction_volume=expected_transaction_volume
        )
        response = self.create_use_case_response(transactions=[expected_transaction])
        view_model = self.presenter.present(response)
        presented_transaction = view_model.transactions[0]
        self.assertIsInstance(presented_transaction.transaction_volume, Decimal)
        self.assertEqual(
            presented_transaction.transaction_volume,
            expected_transaction_volume,
        )

    def test_that_correct_string_is_shown_for_each_account_type(self) -> None:
        account_types = [
            AccountTypes.p,
            AccountTypes.r,
            AccountTypes.a,
            AccountTypes.prd,
        ]
        for account_type in account_types:
            with self.subTest():
                expected_transaction = self._get_single_transaction_info(
                    account_type=account_type
                )
                response = self.create_use_case_response(
                    transactions=[expected_transaction]
                )
                view_model = self.presenter.present(response)
                presented_transaction = view_model.transactions[0]
                self.assertEqual(
                    presented_transaction.account,
                    self._get_account_name(account_type),
                )

    def test_that_transaction_purpose_is_shown_as_correct_string(self) -> None:
        expected_purpose = "purpose test"
        expected_transaction = self._get_single_transaction_info(
            purpose=expected_purpose
        )
        response = self.create_use_case_response(transactions=[expected_transaction])
        view_model = self.presenter.present(response)
        presented_transaction = view_model.transactions[0]
        self.assertIsInstance(presented_transaction.purpose, str)
        self.assertEqual(presented_transaction.purpose, expected_purpose)

    def test_return_two_transactions_when_two_transactions_took_place(self) -> None:
        response = self.create_use_case_response(
            transactions=[
                self._get_single_transaction_info(),
                self._get_single_transaction_info(),
            ]
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self.create_use_case_response(transactions=[])
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_company_accounts(
        self,
    ) -> None:
        response = self.create_use_case_response()
        view_model = self.presenter.present(response)
        first_navbar_item = view_model.navbar_items[0]
        assert first_navbar_item.text == self.translator.gettext("Accounts")
        assert first_navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_all_transactions_and_url_not_set(self) -> None:
        response = self.create_use_case_response()
        view_model = self.presenter.present(response)
        second_navbar_item = view_model.navbar_items[1]
        assert second_navbar_item.text == self.translator.gettext("All transactions")
        assert second_navbar_item.url is None

    def create_use_case_response(
        self,
        transactions: Optional[list[TransactionInfo]] = None,
        company_id: Optional[UUID] = None,
    ) -> GetCompanyTransactionsResponse:
        if transactions is None:
            transactions = []
        if company_id is None:
            company_id = self.company_generator.create_company()
        return GetCompanyTransactionsResponse(
            transactions=transactions,
            company_id=company_id,
        )

    def _get_single_transaction_info(
        self,
        transaction_type: Optional[TransactionTypes] = None,
        date: Optional[datetime] = None,
        transaction_volume: Optional[Decimal] = None,
        account_type: Optional[AccountTypes] = None,
        purpose: Optional[str] = None,
    ) -> TransactionInfo:
        if transaction_type is None:
            transaction_type = TransactionTypes.credit_for_fixed_means
        if date is None:
            date = datetime.now()
        if transaction_volume is None:
            transaction_volume = Decimal(10)
        if account_type is None:
            account_type = AccountTypes.p
        if purpose is None:
            purpose = "Test purpose"
        return TransactionInfo(
            transaction_type=transaction_type,
            date=date,
            transaction_volume=transaction_volume,
            account_type=account_type,
            purpose=purpose,
        )

    def _get_transaction_name(self, transaction_type: TransactionTypes):
        transaction_dict_test_impl = dict(
            credit_for_wages=self.translator.gettext("Credit for wages"),
            payment_of_wages=self.translator.gettext("Payment of wages"),
            credit_for_fixed_means=self.translator.gettext(
                "Credit for fixed means of production"
            ),
            consumption_of_fixed_means=self.translator.gettext(
                "Consumption of fixed means of production"
            ),
            credit_for_liquid_means=self.translator.gettext(
                "Credit for liquid means of production"
            ),
            consumption_of_liquid_means=self.translator.gettext(
                "Consumption of liquid means of production"
            ),
            expected_sales=self.translator.gettext("Debit expected sales"),
            sale_of_consumer_product=self.translator.gettext(
                "Sale of consumer product"
            ),
            sale_of_fixed_means=self.translator.gettext(
                "Sale of fixed means of production"
            ),
            sale_of_liquid_means=self.translator.gettext(
                "Sale of liquid means of production"
            ),
        )
        return transaction_dict_test_impl[transaction_type.name]

    def _get_account_name(self, account_type: AccountTypes):
        type_to_string_dict_test_impl = {
            AccountTypes.p: self.translator.gettext("Account p"),
            AccountTypes.r: self.translator.gettext("Account r"),
            AccountTypes.a: self.translator.gettext("Account a"),
            AccountTypes.prd: self.translator.gettext("Account prd"),
        }
        return type_to_string_dict_test_impl[account_type]
