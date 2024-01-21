from dataclasses import dataclass

from arbeitszeit.use_cases import query_private_consumptions as use_case
from arbeitszeit_web.session import Session, UserRole


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class QueryPrivateConsumptionsController:
    session: Session

    def process_request(self) -> use_case.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        match self.session.get_user_role():
            case UserRole.member:
                return use_case.Request(member=user_id)
        return InvalidRequest(status_code=403)
