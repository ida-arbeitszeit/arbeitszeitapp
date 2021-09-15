from dataclasses import dataclass

from arbeitszeit.use_cases import StatisticsResponse


@dataclass
class GetStatisticsViewModel:
    registered_companies_count: str
    registered_members_count: str
    active_plans_count: str
    active_plans_public_count: str
    average_timeframe_days: str
    products_on_marketplace_count: str
    planned_work_hours: str
    planned_resources_hours: str
    planned_means_hours: str


class GetStatisticsPresenter:
    def present(self, use_case_response: StatisticsResponse) -> GetStatisticsViewModel:
        return GetStatisticsViewModel(
            planned_resources_hours=f"{use_case_response.planned_resources:.2f}",
            planned_work_hours=f"{use_case_response.planned_work:.2f}",
            planned_means_hours=f"{use_case_response.planned_means:.2f}",
            products_on_marketplace_count=str(
                use_case_response.products_on_marketplace_count
            ),
            registered_companies_count=str(
                use_case_response.registered_companies_count
            ),
            registered_members_count=str(use_case_response.registered_members_count),
            active_plans_count=str(use_case_response.active_plans_count),
            active_plans_public_count=str(use_case_response.active_plans_public_count),
            average_timeframe_days=f"{use_case_response.avg_timeframe:.2f}",
        )
