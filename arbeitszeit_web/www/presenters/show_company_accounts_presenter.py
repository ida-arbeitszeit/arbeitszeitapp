from dataclasses import dataclass

from arbeitszeit.use_cases.show_company_accounts import ShowCompanyAccountsResponse
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    balance_fixed: str
    is_fixed_positive: bool
    balance_liquid: str
    is_liquid_positive: bool
    balance_work: str
    is_work_positive: bool
    balance_product: str
    is_product_positive: bool
    url_to_account_p: str
    url_to_account_r: str
    url_to_account_a: str
    url_to_account_prd: str
    url_to_all_transactions: str


@dataclass
class ShowCompanyAccountsPresenter:
    url_index: UrlIndex

    def present(self, use_case_response: ShowCompanyAccountsResponse) -> ViewModel:
        balances = [str(round(balance, 2)) for balance in use_case_response.balances]
        signs = [balance >= 0 for balance in use_case_response.balances]

        return ViewModel(
            balance_fixed=balances[0],
            is_fixed_positive=signs[0],
            balance_liquid=balances[1],
            is_liquid_positive=signs[1],
            balance_work=balances[2],
            is_work_positive=signs[2],
            balance_product=balances[3],
            is_product_positive=signs[3],
            url_to_account_p=self.url_index.get_company_account_p_url(
                company_id=use_case_response.company
            ),
            url_to_account_r=self.url_index.get_company_account_r_url(
                company_id=use_case_response.company
            ),
            url_to_account_a=self.url_index.get_company_account_a_url(
                company_id=use_case_response.company
            ),
            url_to_account_prd=self.url_index.get_company_account_prd_url(),
            url_to_all_transactions=self.url_index.get_company_transactions_url(
                company_id=use_case_response.company
            ),
        )
