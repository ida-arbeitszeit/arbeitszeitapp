from dataclasses import dataclass

from arbeitszeit.use_cases import query_private_consumptions as use_case
from arbeitszeit_web.session import Session, UserRole


@dataclass
class QueryPrivateConsumptionsController:
    session: Session

    def process_request(self) -> use_case.Request | None:
        match self.session.get_user_role():
            case UserRole.member:
                user_id = self.session.get_current_user()
                assert user_id
                return use_case.Request(member=user_id)
            case _:
                return None
