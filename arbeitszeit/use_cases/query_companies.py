from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Iterable, List, Optional, TypeVar
from uuid import UUID

from arbeitszeit.records import Company, EmailAddress
from arbeitszeit.repositories import CompanyResult, DatabaseGateway, QueryResult

QueryT = TypeVar("QueryT", bound=QueryResult)


class CompanyFilter(enum.Enum):
    by_name = enum.auto()
    by_email = enum.auto()


@dataclass
class CompanyQueryResponse:
    results: List[QueriedCompany]
    total_results: int
    request: QueryCompaniesRequest


@dataclass
class QueriedCompany:
    company_id: UUID
    company_email: str
    company_name: str


@dataclass
class QueryCompaniesRequest:
    query_string: Optional[str]
    filter_category: CompanyFilter
    offset: Optional[int]
    limit: Optional[int]


@dataclass
class QueryCompanies:
    database: DatabaseGateway

    def __call__(self, request: QueryCompaniesRequest) -> CompanyQueryResponse:
        companies: Iterable[Company]
        query = request.query_string
        filter_by = request.filter_category
        companies = _filter_companies(self.database.get_companies(), query, filter_by)
        total_results = len(companies)
        results = [
            self._create_response_model(company, mail)
            for company, mail in _limit_results(
                companies.joined_with_email_address(),
                limit=request.limit,
                offset=request.offset,
            )
        ]
        return CompanyQueryResponse(
            results=results, total_results=total_results, request=request
        )

    def _create_response_model(
        self, company: Company, email: EmailAddress
    ) -> QueriedCompany:
        return QueriedCompany(
            company_id=company.id,
            company_email=email.address,
            company_name=company.name,
        )


def _filter_companies(
    companies: CompanyResult, query: Optional[str], filter_by: CompanyFilter
) -> CompanyResult:
    if query:
        if filter_by == CompanyFilter.by_name:
            companies = companies.with_name_containing(query)
        else:
            companies = companies.with_email_containing(query)
    return companies


def _limit_results(
    companies: QueryT, *, limit: Optional[int] = None, offset: Optional[int] = None
) -> QueryT:
    if offset is not None:
        companies = companies.offset(n=offset)
    if limit is not None:
        companies = companies.limit(n=limit)
    return companies
