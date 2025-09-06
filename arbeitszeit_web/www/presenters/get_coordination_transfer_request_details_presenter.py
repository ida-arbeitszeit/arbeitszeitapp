from dataclasses import dataclass

from arbeitszeit.use_cases.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsUseCase as UseCase,
)
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetCoordinationTransferRequestDetailsPresenter:
    @dataclass
    class ViewModel:
        request_date: str
        cooperation_url: str
        cooperation_name: str
        candidate_url: str
        candidate_name: str
        current_user_is_candidate: bool
        request_is_pending: bool
        request_status: str

    datetime_formatter: DatetimeFormatter
    session: Session
    url_index: UrlIndex
    translator: Translator

    def present(self, response: UseCase.Response) -> ViewModel:
        current_user = self.session.get_current_user()
        assert current_user
        return self.ViewModel(
            request_date=self.datetime_formatter.format_datetime(
                response.request_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            cooperation_url=self.url_index.get_coop_summary_url(
                coop_id=response.cooperation_id
            ),
            cooperation_name=response.cooperation_name,
            candidate_url=self.url_index.get_company_summary_url(
                company_id=response.candidate_id
            ),
            candidate_name=response.candidate_name,
            current_user_is_candidate=current_user == response.candidate_id,
            request_is_pending=response.request_is_pending,
            request_status=(
                self.translator.gettext("Pending")
                if response.request_is_pending
                else self.translator.gettext("Closed")
            ),
        )
