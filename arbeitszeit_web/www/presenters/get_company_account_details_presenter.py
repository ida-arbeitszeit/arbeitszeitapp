from dataclasses import dataclass

from arbeitszeit.use_cases import get_user_account_details as use_case


@dataclass
class ViewModel:
    email_address: str
    user_id: str


class GetCompanyAccountDetailsPresenter:
    def render_company_account_details(self, response: use_case.Response) -> ViewModel:
        assert response.user_info
        return ViewModel(
            email_address=response.user_info.email_address,
            user_id=str(response.user_info.id),
        )
