from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit.use_cases import StatisticsResponse
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.translator import Translator


@dataclass
class GetStatisticsViewModel:
    registered_companies_count: str
    registered_members_count: str
    cooperations_count: str
    certificates_count: str
    available_product: str
    active_plans_count: str
    active_plans_public_count: str
    average_timeframe_days: str
    planned_work_hours: str
    planned_resources_hours: str
    planned_means_hours: str

    barplot_certificates: str
    barplot_means_of_production: str
    barplot_plans: str


@dataclass
class GetStatisticsPresenter:
    trans: Translator
    plotter: Plotter
    colors: Colors

    def present(self, use_case_response: StatisticsResponse) -> GetStatisticsViewModel:
        average_timeframe = self.trans.ngettext(
            "%(num).2f day", "%(num).2f days", use_case_response.avg_timeframe
        )
        planned_work = self.trans.ngettext(
            "%(num).2f hour", "%(num).2f hours", use_case_response.planned_work
        )
        planned_liquid_means = self.trans.ngettext(
            "%(num).2f hour", "%(num).2f hours", use_case_response.planned_resources
        )
        planned_fixed_means = self.trans.ngettext(
            "%(num).2f hour", "%(num).2f hours", use_case_response.planned_means
        )
        return GetStatisticsViewModel(
            planned_resources_hours=planned_liquid_means,
            planned_work_hours=planned_work,
            planned_means_hours=planned_fixed_means,
            registered_companies_count=str(
                use_case_response.registered_companies_count
            ),
            registered_members_count=str(use_case_response.registered_members_count),
            cooperations_count=str(use_case_response.cooperations_count),
            certificates_count="%(num).2f"
            % dict(num=use_case_response.certificates_count),
            available_product="%(num).2f"
            % dict(num=use_case_response.available_product),
            active_plans_count=str(use_case_response.active_plans_count),
            active_plans_public_count=str(use_case_response.active_plans_public_count),
            average_timeframe_days=average_timeframe,
            barplot_certificates=self.plotter.create_bar_plot(
                x_coordinates=[
                    self.trans.gettext("Work certificates"),
                    self.trans.gettext("Available product"),
                ],
                height_of_bars=[
                    use_case_response.certificates_count,
                    use_case_response.available_product,
                ],
                colors_of_bars=[self.colors.primary, self.colors.info],
                fig_size=(5, 4),
                y_label=self.trans.gettext("Hours"),
            ),
            barplot_means_of_production=self.plotter.create_bar_plot(
                x_coordinates=[
                    self.trans.gettext("Feste PM"),
                    self.trans.gettext("Flüssige PM"),
                    self.trans.gettext("Arbeit"),
                ],
                height_of_bars=[
                    use_case_response.planned_means,
                    use_case_response.planned_resources,
                    use_case_response.planned_work,
                ],
                colors_of_bars=[
                    self.colors.primary,
                    self.colors.info,
                    self.colors.danger,
                ],
                fig_size=(5, 4),
                y_label=self.trans.gettext("Hours"),
            ),
            barplot_plans=self.plotter.create_bar_plot(
                x_coordinates=[
                    self.trans.gettext("Produktive Pläne"),
                    self.trans.gettext("Öffentliche Pläne"),
                ],
                height_of_bars=[
                    Decimal(
                        use_case_response.active_plans_count
                        - use_case_response.active_plans_public_count
                    ),
                    Decimal(use_case_response.active_plans_public_count),
                ],
                colors_of_bars=list(self.colors.get_all_defined_colors().values()),
                fig_size=(5, 4),
                y_label=self.trans.gettext("Amount"),
            ),
        )
