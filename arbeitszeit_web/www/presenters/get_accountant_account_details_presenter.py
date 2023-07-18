from dataclasses import dataclass

from arbeitszeit.use_cases import get_user_account_details as use_case


@dataclass
class ViewModel:
    user_id: str
    email_address: str


class GetAccountantAccountDetailsPresenter:
    def render_accountant_account_details(
        self, response: use_case.Response
    ) -> ViewModel:
        assert response.user_info
        return ViewModel(
            user_id=str(response.user_info.id),
            email_address=response.user_info.email_address,
        )
