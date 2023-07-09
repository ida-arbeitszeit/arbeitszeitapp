from dataclasses import dataclass

from arbeitszeit.use_cases import get_user_account_details as use_case
from arbeitszeit_web.session import Session, UserRole


@dataclass
class GetCompanyAccountDetailsController:
    session: Session

    def parse_web_request(self) -> use_case.Request:
        user_id = self.session.get_current_user()
        if self.session.get_user_role() != UserRole.company or not user_id:
            raise Exception()
        return use_case.Request(user_id=user_id)
