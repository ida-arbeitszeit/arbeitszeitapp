from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from arbeitszeit.use_cases import DraftQueryResponse


@dataclass
class ResultTableRow:
    id: str
    creation_date: str
    product_name: str
    description: List[str]


@dataclass
class ResultsTable:
    rows: List[ResultTableRow]


@dataclass
class QueryDraftsViewModel:
    results: ResultsTable
    show_results: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QueryDraftsPresenter:
    def present(self, response: DraftQueryResponse) -> QueryDraftsViewModel:
        show_results = bool(response.results)
        results = ResultsTable(
            rows=[
                ResultTableRow(
                    id=str(result.id),
                    creation_date=self.__format_date(result.creation_date),
                    product_name=result.product_name,
                    description=result.description.splitlines(),
                )
                for result in response.results
            ]
        )
        return QueryDraftsViewModel(results=results, show_results=show_results)

    def __format_date(self, date: Optional[datetime]) -> str:
        return f"{date.strftime('%d.%m.%y')}" if date else "–"
