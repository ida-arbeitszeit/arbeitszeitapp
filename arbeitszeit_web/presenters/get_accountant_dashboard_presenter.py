from dataclasses import dataclass

from arbeitszeit.use_cases.get_accountant_dashboard import GetAccountantDashboardUseCase
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetAccountantDashboardPresenter:
    @dataclass
    class ViewModel:
        unreviewed_plans_view_url: str
        name: str
        accountant_id: str
        email: str

    url_index: UrlIndex

    def create_dashboard_view_model(
        self, response: GetAccountantDashboardUseCase.Response
    ) -> ViewModel:
        return self.ViewModel(
            unreviewed_plans_view_url=self.url_index.get_unreviewed_plans_list_view_url(),
            name=response.name,
            accountant_id=f"{response.accountant_id}",
            email=response.email,
        )
