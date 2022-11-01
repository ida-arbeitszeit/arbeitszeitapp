from dataclasses import dataclass

from injector import inject

from arbeitszeit_web.url_index import UrlIndex


@inject
@dataclass
class GetAccountantDashboardPresenter:
    @dataclass
    class ViewModel:
        unreviewed_plans_view_url: str

    url_index: UrlIndex

    def create_dashboard_view_model(self) -> ViewModel:
        return self.ViewModel(
            unreviewed_plans_view_url=self.url_index.get_unreviewed_plans_list_view_url(),
        )
