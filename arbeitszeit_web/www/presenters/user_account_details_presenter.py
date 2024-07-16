from dataclasses import dataclass

from arbeitszeit.use_cases import get_user_account_details as use_case
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    user_id: str
    email_address: str
    request_email_address_change_url: str


@dataclass
class UserAccountDetailsPresenter:
    url_index: UrlIndex

    def render_user_account_details(self, response: use_case.Response) -> ViewModel:
        assert response.user_info
        return ViewModel(
            user_id=str(response.user_info.id),
            email_address=response.user_info.email_address,
            request_email_address_change_url=self.url_index.get_request_change_email_url(),
        )
