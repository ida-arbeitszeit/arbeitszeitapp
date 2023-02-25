from dataclasses import dataclass
from typing import Optional

from arbeitszeit.entities import Company
from arbeitszeit.use_cases import (
    CompanyFilter,
    CompanyQueryResponse,
    QueryCompanies,
    QueryCompaniesRequest,
)
from tests.use_cases.base_test_case import BaseTestCase


class TestQueryCompanies(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_companies = self.injector.get(QueryCompanies)

    def company_in_results(
        self, company: Company, response: CompanyQueryResponse
    ) -> bool:
        return any(
            (
                company.name == result.company_name
                and company.email == result.company_email
                for result in response.results
            )
        )

    def test_that_no_company_is_returned_when_searching_an_empty_repository(self):
        response = self.query_companies(make_request(None, CompanyFilter.by_name))
        assert not response.results
        response = self.query_companies(make_request(None, CompanyFilter.by_email))
        assert not response.results

    def test_that_company_is_returned_when_searching_without_query(self):
        expected_company = self.company_generator.create_company_entity(
            name="My Company"
        )
        response = self.query_companies(make_request(None, CompanyFilter.by_name))
        assert self.company_in_results(expected_company, response)

    def test_that_company_is_returned_when_searching_with_empty_query_string(self):
        expected_company = self.company_generator.create_company_entity(
            name="My Company"
        )
        response = self.query_companies(make_request("", CompanyFilter.by_name))
        assert self.company_in_results(expected_company, response)

    def test_that_companies_where_name_is_exact_match_are_returned(self):
        expected_company = self.company_generator.create_company_entity(
            name="My Company"
        )
        response = self.query_companies(
            make_request("My Company", CompanyFilter.by_name)
        )
        assert self.company_in_results(expected_company, response)

    def test_query_substring_of_name_returns_correct_result(self):
        expected_company = self.company_generator.create_company_entity(
            name="My Company"
        )
        response = self.query_companies(make_request("Company", CompanyFilter.by_name))
        assert self.company_in_results(expected_company, response)

    def test_that_companies_where_name_not_match_are_not_returned(self):
        self.company_generator.create_company_entity(name="My Company")
        response = self.query_companies(make_request("Factory", CompanyFilter.by_name))
        assert not response.results

    def test_that_capitalization_is_ignored_in_name(self):
        expected_company = self.company_generator.create_company_entity(
            name="My Company"
        )
        response = self.query_companies(make_request("company", CompanyFilter.by_name))
        assert self.company_in_results(expected_company, response)

    def test_that_companies_where_email_is_exact_match_are_returned(self):
        expected_company = self.company_generator.create_company_entity(
            email="company@provider.de"
        )
        response = self.query_companies(
            make_request("company@provider.de", CompanyFilter.by_email)
        )
        assert self.company_in_results(expected_company, response)

    def test_query_substring_of_email_returns_correct_result(self):
        expected_company = self.company_generator.create_company_entity(
            email="company@provider.de"
        )
        response = self.query_companies(make_request("company", CompanyFilter.by_email))
        assert self.company_in_results(expected_company, response)

    def test_that_companies_where_email_not_match_are_not_returned(self):
        self.company_generator.create_company_entity(email="company@provider.de")
        response = self.query_companies(make_request("factory", CompanyFilter.by_email))
        assert not response.results

    def test_that_capitalization_is_ignored_in_email(self):
        expected_company = self.company_generator.create_company_entity(
            email="company@provider.de"
        )
        response = self.query_companies(make_request("Company", CompanyFilter.by_email))
        assert self.company_in_results(expected_company, response)


class TestPagination(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_companies = self.injector.get(QueryCompanies)


def make_request(query: Optional[str], category: CompanyFilter):
    return QueryCompaniesRequestTestImpl(
        query=query,
        filter_category=category,
    )


@dataclass
class QueryCompaniesRequestTestImpl(QueryCompaniesRequest):
    query: Optional[str]
    filter_category: CompanyFilter
    offset: Optional[int] = None
    limit: Optional[int] = None

    def get_query_string(self) -> Optional[str]:
        return self.query

    def get_filter_category(self) -> CompanyFilter:
        return self.filter_category

    def get_offset(self) -> Optional[int]:
        return self.offset

    def get_limit(self) -> Optional[int]:
        return self.limit
