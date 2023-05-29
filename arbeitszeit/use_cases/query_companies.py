from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional
from uuid import UUID

from arbeitszeit.entities import Company
from arbeitszeit.repositories import CompanyResult, DatabaseGateway


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


class QueryCompaniesRequest(ABC):
    @abstractmethod
    def get_query_string(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_filter_category(self) -> CompanyFilter:
        pass

    @abstractmethod
    def get_offset(self) -> Optional[int]:
        pass

    @abstractmethod
    def get_limit(self) -> Optional[int]:
        pass


@dataclass
class QueryCompanies:
    database: DatabaseGateway

    def __call__(self, request: QueryCompaniesRequest) -> CompanyQueryResponse:
        companies: Iterable[Company]
        query = request.get_query_string()
        filter_by = request.get_filter_category()
        companies = self.database.get_companies()
        companies = self._filter_companies(companies, query, filter_by)
        total_results = len(companies)
        companies = self._limit_results(companies, request)
        results = [self._company_to_response_model(company) for company in companies]
        return CompanyQueryResponse(
            results=results, total_results=total_results, request=request
        )

    def _filter_companies(
        self, companies: CompanyResult, query: Optional[str], filter_by: CompanyFilter
    ) -> CompanyResult:
        if query is None:
            pass
        elif filter_by == CompanyFilter.by_name:
            companies = companies.with_name_containing(query)
        else:
            companies = companies.with_email_containing(query)
        return companies

    def _limit_results(
        self, companies: CompanyResult, request: QueryCompaniesRequest
    ) -> CompanyResult:
        offset = request.get_offset()
        limit = request.get_limit()
        if offset is not None:
            companies = companies.offset(n=offset)
        if limit is not None:
            companies = companies.limit(n=limit)
        return companies

    def _company_to_response_model(self, company: Company) -> QueriedCompany:
        return QueriedCompany(
            company_id=company.id,
            company_email=company.email,
            company_name=company.name,
        )
