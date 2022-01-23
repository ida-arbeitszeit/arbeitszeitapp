from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.entities import AccountTypes
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactionsResponse,
    TransactionInfo,
)
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter

DEFAULT_INFO1 = TransactionInfo(
    type_of_transaction=TransactionTypes.credit_for_fixed_means,
    date=datetime.now(),
    transaction_volume=Decimal(10),
    account_type=AccountTypes.p,
    purpose="Test purpose",
)

DEFAULT_INFO2 = TransactionInfo(
    type_of_transaction=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    account_type=AccountTypes.a,
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = GetCompanyTransactionsPresenter()

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = GetCompanyTransactionsResponse(transactions=[])
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self):
        response = GetCompanyTransactionsResponse(transactions=[DEFAULT_INFO1])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        trans = view_model.transactions[0]
        self.assertEqual(
            trans.transaction_type, DEFAULT_INFO1.type_of_transaction.value
        )
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, DEFAULT_INFO1.transaction_volume)
        self.assertEqual(
            trans.account, type_to_string_dict_test_impl[DEFAULT_INFO1.account_type]
        )
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = GetCompanyTransactionsResponse(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2]
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)


type_to_string_dict_test_impl = {
    AccountTypes.p: "Account p",
    AccountTypes.r: "Account r",
    AccountTypes.a: "Account a",
    AccountTypes.prd: "Account prd",
}
