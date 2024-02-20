from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.use_cases.show_company_accounts import ShowCompanyAccountsResponse
from arbeitszeit_web.www.presenters.show_company_accounts_presenter import (
    ShowCompanyAccountsPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ShowCompanyAccountsPresenterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.presenter = self.injector.get(ShowCompanyAccountsPresenter)

    def test_show_correct_balance_string_for_balances(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(presentation.balance_fixed, "0.00")
        self.assertEqual(presentation.balance_liquid, "-1.00")
        self.assertEqual(presentation.balance_work, "2.01")
        self.assertEqual(presentation.balance_product, "2.50")

    def test_show_correct_signs_for_balances(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(presentation.is_fixed_positive, True)
        self.assertEqual(presentation.is_liquid_positive, False)
        self.assertEqual(presentation.is_work_positive, True)
        self.assertEqual(presentation.is_product_positive, True)

    def test_view_model_contains_url_to_account_p_of_the_requested_company(
        self,
    ) -> None:
        company = uuid4()
        presentation = self.presenter.present(
            self.create_use_case_response(company=company)
        )
        self.assertEqual(
            presentation.url_to_account_p,
            self.url_index.get_company_account_p_url(company_id=company),
        )

    def test_view_model_contains_url_to_account_r(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(
            presentation.url_to_account_r, self.url_index.get_company_account_r_url()
        )

    def test_view_model_contains_url_to_account_a(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(
            presentation.url_to_account_a, self.url_index.get_company_account_a_url()
        )

    def test_view_model_contains_url_to_account_prd(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(
            presentation.url_to_account_prd,
            self.url_index.get_company_account_prd_url(),
        )

    def test_view_model_contains_url_to_all_transactions(self) -> None:
        presentation = self.presenter.present(self.create_use_case_response())
        self.assertEqual(
            presentation.url_to_all_transactions,
            self.url_index.get_company_transactions_url(),
        )

    def create_use_case_response(
        self, company: UUID | None = None
    ) -> ShowCompanyAccountsResponse:
        if company is None:
            company = uuid4()
        balances = [Decimal(0), Decimal(-1), Decimal(2.0051), Decimal(2.5)]
        return ShowCompanyAccountsResponse(balances=balances, company=company)
