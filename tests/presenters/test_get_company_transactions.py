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
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

DEFAULT_INFO1 = TransactionInfo(
    transaction_type=TransactionTypes.credit_for_fixed_means,
    date=datetime.now(),
    transaction_volume=Decimal(10),
    account_type=AccountTypes.p,
    purpose="Test purpose",
)

DEFAULT_INFO2 = TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    account_type=AccountTypes.a,
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(GetCompanyTransactionsPresenter)

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
            trans.transaction_type,
            self._get_transaction_name(DEFAULT_INFO1.transaction_type),
        )
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, DEFAULT_INFO1.transaction_volume)
        self.assertEqual(
            trans.account, self._get_account_name(DEFAULT_INFO1.account_type)
        )
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = GetCompanyTransactionsResponse(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2]
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def _get_transaction_name(self, transaction_type: TransactionTypes):
        transaction_dict_test_impl = dict(
            credit_for_wages=self.translator.gettext("Credit for wages"),
            payment_of_wages=self.translator.gettext("Payment of wages"),
            incoming_wages=self.translator.gettext("Incoming wages"),
            credit_for_fixed_means=self.translator.gettext(
                "Credit for fixed means of production"
            ),
            payment_of_fixed_means=self.translator.gettext(
                "Payment of fixed means of production"
            ),
            credit_for_liquid_means=self.translator.gettext(
                "Credit for liquid means of production"
            ),
            payment_of_liquid_means=self.translator.gettext(
                "Payment of liquid means of production"
            ),
            expected_sales=self.translator.gettext("Debit expected sales"),
            sale_of_consumer_product=self.translator.gettext(
                "Sale of consumer product"
            ),
            payment_of_consumer_product=self.translator.gettext(
                "Payment of consumer product"
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
