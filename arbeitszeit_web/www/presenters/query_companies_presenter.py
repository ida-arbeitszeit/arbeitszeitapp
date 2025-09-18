from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors.query_companies import CompanyQueryResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pagination import Pagination, Paginator
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ResultTableRow:
    company_id: str
    company_name: str
    company_email: str
    company_summary_url: str


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryCompaniesViewModel:
    results: ResultsTable
    show_results: bool
    pagination: Pagination


@dataclass
class QueryCompaniesPresenter:
    user_notifier: Notifier
    url_index: UrlIndex
    translator: Translator
    request: Request

    def present(self, response: CompanyQueryResponse) -> QueryCompaniesViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.translator.gettext("No results"))
        return QueryCompaniesViewModel(
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        company_id=str(result.company_id),
                        company_name=result.company_name,
                        company_email=result.company_email,
                        company_summary_url=self.url_index.get_company_summary_url(
                            company_id=result.company_id,
                        ),
                    )
                    for result in response.results
                ],
            ),
            pagination=self._create_pagination(response),
        )

    def get_empty_view_model(self) -> QueryCompaniesViewModel:
        return QueryCompaniesViewModel(
            results=ResultsTable(rows=[]),
            show_results=False,
            pagination=Pagination(is_visible=False, pages=[]),
        )

    def _create_pagination(self, response: CompanyQueryResponse) -> Pagination:
        paginator = Paginator(
            request=self.request,
            total_results=response.total_results,
        )
        return Pagination(
            is_visible=paginator.number_of_pages > 1,
            pages=paginator.get_pages(),
        )
