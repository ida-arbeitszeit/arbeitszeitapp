from decimal import Decimal

from arbeitszeit.use_cases.show_company_accounts import (
    ShowCompanyAccounts,
    ShowCompanyAccountsRequest,
)

from ..data_generators import CompanyGenerator, TransactionGenerator
from .dependency_injection import injection_test


@injection_test
def test_that_list_of_balances_has_four_entries_when_no_transactions_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company_record()
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    assert len(response.balances) == 4


@injection_test
def test_that_all_balances_are_zero_when_no_transactions_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company_record()
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    for balance in response.balances:
        assert balance == Decimal(0)


@injection_test
def test_that_balance_of_mean_account_reflects_transaction_that_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company_record()
    transaction_generator.create_transaction(
        sending_account=company.means_account, amount_sent=Decimal(10)
    )
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    assert response.balances[0] == Decimal(-10)


@injection_test
def test_that_balance_of_raw_material_account_reflects_transaction_that_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company_record()
    transaction_generator.create_transaction(
        sending_account=company.raw_material_account, amount_sent=Decimal(10)
    )
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    assert response.balances[1] == Decimal(-10)


@injection_test
def test_that_balance_of_work_account_reflects_transaction_that_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company_record()
    transaction_generator.create_transaction(
        sending_account=company.work_account, amount_sent=Decimal(10)
    )
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    assert response.balances[2] == Decimal(-10)


@injection_test
def test_that_balance_of_product_account_reflects_transaction_that_took_place(
    use_case: ShowCompanyAccounts,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company_record()
    transaction_generator.create_transaction(
        receiving_account=company.product_account, amount_sent=Decimal(10)
    )
    response = use_case(request=ShowCompanyAccountsRequest(company=company.id))
    assert response.balances[3] == Decimal(10)
