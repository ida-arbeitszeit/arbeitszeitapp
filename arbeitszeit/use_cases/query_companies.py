from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional
from uuid import UUID

from arbeitszeit.entities import Company
from arbeitszeit.repositories import CompanyRepository


class CompanyFilter(enum.Enum):
    by_name = enum.auto()
    by_email = enum.auto()


@dataclass
class CompanyQueryResponse:
    results: List[QueriedCompany]


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
    company_repository: CompanyRepository

    def __call__(self, request: QueryCompaniesRequest) -> CompanyQueryResponse:
        found_companies: Iterable[Company]
        query = request.get_query_string()
        filter_by = request.get_filter_category()
        found_companies = self.company_repository.get_companies()
        if query is None:
            pass
        elif filter_by == CompanyFilter.by_name:
            found_companies = found_companies.with_name_containing(query)
        else:
            found_companies = found_companies.with_email_containing(query)
        results = [
            self._company_to_response_model(company) for company in found_companies
        ]
        return CompanyQueryResponse(
            results=results,
        )

    def _company_to_response_model(self, company: Company) -> QueriedCompany:
        return QueriedCompany(
            company_id=company.id,
            company_email=company.email,
            company_name=company.name,
        )
