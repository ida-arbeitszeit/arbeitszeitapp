from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.interactors.get_statistics import StatisticsResponse
from arbeitszeit_web.colors import HexColors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetStatisticsViewModel:
    registered_companies_count: str
    registered_members_count: str
    cooperations_count: str
    certificates_count: str
    available_product_in_productive_sector: str
    active_plans_count: str
    active_plans_public_count: str
    average_timeframe_days: str
    planned_work_hours: str
    planned_resources_hours: str
    planned_means_hours: str
    payout_factor: str
    psf_balance: str

    barplot_for_certificates_url: str
    barplot_means_of_production_url: str
    barplot_plans_url: str


@dataclass
class GetStatisticsPresenter:
    translator: Translator
    plotter: Plotter
    colors: HexColors
    url_index: UrlIndex
    datetime_service: DatetimeService

    def present(
        self, interactor_response: StatisticsResponse
    ) -> GetStatisticsViewModel:
        average_timeframe = self.translator.gettext("%(num).2f days") % dict(
            num=interactor_response.avg_timeframe
        )
        planned_work = self.translator.gettext("%(num).2f hours") % dict(
            num=interactor_response.planned_work
        )
        planned_liquid_means = self.translator.gettext("%(num).2f hours") % dict(
            num=interactor_response.planned_resources
        )
        planned_fixed_means = self.translator.gettext("%(num).2f hours") % dict(
            num=interactor_response.planned_means
        )
        return GetStatisticsViewModel(
            planned_resources_hours=planned_liquid_means,
            planned_work_hours=planned_work,
            planned_means_hours=planned_fixed_means,
            registered_companies_count=str(
                interactor_response.registered_companies_count
            ),
            registered_members_count=str(interactor_response.registered_members_count),
            cooperations_count=str(interactor_response.cooperations_count),
            certificates_count="%(num).2f"
            % dict(num=interactor_response.certificates_count),
            available_product_in_productive_sector="%(num).2f"
            % dict(num=interactor_response.available_product_in_productive_sector),
            active_plans_count=str(interactor_response.active_plans_count),
            active_plans_public_count=str(
                interactor_response.active_plans_public_count
            ),
            average_timeframe_days=average_timeframe,
            payout_factor=self._format_payout_factor(interactor_response.payout_factor),
            psf_balance=self._format_psf_balance(interactor_response.psf_balance),
            barplot_for_certificates_url=self.url_index.get_global_barplot_for_certificates_url(
                interactor_response.certificates_count,
                interactor_response.available_product_in_productive_sector,
            ),
            barplot_means_of_production_url=self.url_index.get_global_barplot_for_means_of_production_url(
                interactor_response.planned_means,
                interactor_response.planned_resources,
                interactor_response.planned_work,
            ),
            barplot_plans_url=self.url_index.get_global_barplot_for_plans_url(
                (
                    interactor_response.active_plans_count
                    - interactor_response.active_plans_public_count
                ),
                interactor_response.active_plans_public_count,
            ),
        )

    def _format_payout_factor(self, payout_factor: Decimal) -> str:
        return str(self._round_with_precision(payout_factor, 2))

    def _format_psf_balance(self, psf_balance: Decimal) -> str:
        return str(self._round_with_precision(psf_balance, 2))

    def _round_with_precision(self, number: Decimal, precision: int) -> Decimal:
        return round(number, precision)
