from dataclasses import dataclass

from arbeitszeit.use_cases.show_my_accounts import ShowMyAccountsRequest
from arbeitszeit_web.session import Session


@dataclass
class ShowMyAccountsController:
    session: Session

    def create_request(self) -> ShowMyAccountsRequest:
        current_user = self.session.get_current_user()
        assert current_user
        return ShowMyAccountsRequest(current_user=current_user)
