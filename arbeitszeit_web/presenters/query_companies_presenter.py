from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from arbeitszeit.use_cases.query_companies import CompanyQueryResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryCompaniesPresenter:
    user_notifier: Notifier
    url_index: UrlIndex
    translator: Translator
    session: Session

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
                            user_role=self.session.get_user_role(),
                            company_id=result.company_id,
                        ),
                    )
                    for result in response.results
                ],
            ),
        )

    def get_empty_view_model(self) -> QueryCompaniesViewModel:
        return QueryCompaniesViewModel(
            results=ResultsTable(rows=[]),
            show_results=False,
        )
