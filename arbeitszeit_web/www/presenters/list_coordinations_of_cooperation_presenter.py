from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase as UseCase,
)
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ListCoordinationsOfCooperationPresenter:
    @dataclass
    class CoordinationInfo:
        coordinator_name: str
        coordinator_url: str
        start_time: str
        end_time: str

    @dataclass
    class ViewModel:
        cooperation_url: str
        cooperation_name: str
        has_coordinations: bool
        coordinations: list[ListCoordinationsOfCooperationPresenter.CoordinationInfo]
        navbar_items: list[NavbarItem]

    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter
    translator: Translator

    def list_coordinations_of_cooperation(
        self, response: UseCase.Response
    ) -> ListCoordinationsOfCooperationPresenter.ViewModel:
        return self.ViewModel(
            cooperation_url=self.url_index.get_coop_summary_url(
                coop_id=response.cooperation_id,
            ),
            cooperation_name=response.cooperation_name,
            has_coordinations=len(response.coordinations) > 0,
            coordinations=[
                self.CoordinationInfo(
                    coordinator_name=coordination.coordinator_name,
                    coordinator_url=self.url_index.get_company_summary_url(
                        company_id=coordination.coordinator_id,
                    ),
                    start_time=self.datetime_formatter.format_datetime(
                        date=coordination.start_time,
                        fmt="%d.%m.%Y %H:%M",
                    ),
                    end_time=(
                        "-"
                        if coordination.end_time is None
                        else self.datetime_formatter.format_datetime(
                            date=coordination.end_time,
                            fmt="%d.%m.%Y %H:%M",
                        )
                    ),
                )
                for coordination in response.coordinations
            ],
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Cooperation"),
                    url=self.url_index.get_coop_summary_url(
                        coop_id=response.cooperation_id,
                    ),
                ),
                NavbarItem(
                    text=self.translator.gettext("Coordinators"),
                    url=None,
                ),
            ],
        )
