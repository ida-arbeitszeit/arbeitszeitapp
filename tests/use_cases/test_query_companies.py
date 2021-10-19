from dataclasses import dataclass
from typing import Optional

from arbeitszeit.entities import Company
from arbeitszeit.use_cases import (
    CompanyFilter,
    CompanyQueryResponse,
    QueryCompanies,
    QueryCompaniesRequest,
)
from tests.data_generators import CompanyGenerator

from .dependency_injection import injection_test


def company_in_results(company: Company, response: CompanyQueryResponse) -> bool:
    return any(
        (
            company.name == result.company_name
            and company.email == result.company_email
            for result in response.results
        )
    )


@injection_test
def test_that_no_company_is_returned_when_searching_an_empty_repository(
    query_companies: QueryCompanies,
):
    response = query_companies(make_request(None, CompanyFilter.by_name))
    assert not response.results
    response = query_companies(make_request(None, CompanyFilter.by_email))
    assert not response.results


@injection_test
def test_that_company_is_returned_when_searching_without_query(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(name="My Company")
    response = query_companies(make_request(None, CompanyFilter.by_name))
    assert company_in_results(expected_company, response)


@injection_test
def test_that_company_is_returned_when_searching_with_empty_query_string(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(name="My Company")
    response = query_companies(make_request("", CompanyFilter.by_name))
    assert company_in_results(expected_company, response)


@injection_test
def test_that_companies_where_name_is_exact_match_are_returned(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(name="My Company")
    response = query_companies(make_request("My Company", CompanyFilter.by_name))
    assert company_in_results(expected_company, response)


@injection_test
def test_query_substring_of_name_returns_correct_result(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(name="My Company")
    response = query_companies(make_request("Company", CompanyFilter.by_name))
    assert company_in_results(expected_company, response)


@injection_test
def test_that_companies_where_name_not_match_are_not_returned(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    company_generator.create_company(name="My Company")
    response = query_companies(make_request("Factory", CompanyFilter.by_name))
    assert not response.results


@injection_test
def test_that_capitalization_is_ignored_in_name(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(name="My Company")
    response = query_companies(make_request("company", CompanyFilter.by_name))
    assert company_in_results(expected_company, response)


@injection_test
def test_that_companies_where_email_is_exact_match_are_returned(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(email="company@provider.de")
    response = query_companies(
        make_request("company@provider.de", CompanyFilter.by_email)
    )
    assert company_in_results(expected_company, response)


@injection_test
def test_query_substring_of_email_returns_correct_result(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(email="company@provider.de")
    response = query_companies(make_request("company", CompanyFilter.by_email))
    assert company_in_results(expected_company, response)


@injection_test
def test_that_companies_where_email_not_match_are_not_returned(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    company_generator.create_company(email="company@provider.de")
    response = query_companies(make_request("factory", CompanyFilter.by_email))
    assert not response.results


@injection_test
def test_that_capitalization_is_ignored_in_email(
    query_companies: QueryCompanies,
    company_generator: CompanyGenerator,
):
    expected_company = company_generator.create_company(email="company@provider.de")
    response = query_companies(make_request("Company", CompanyFilter.by_email))
    assert company_in_results(expected_company, response)


def make_request(query: Optional[str], category: CompanyFilter):
    return QueryCompaniesRequestTestImpl(
        query=query,
        filter_category=category,
    )


@dataclass
class QueryCompaniesRequestTestImpl(QueryCompaniesRequest):
    query: Optional[str]
    filter_category: CompanyFilter

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> CompanyFilter:
        return self.filter_category
