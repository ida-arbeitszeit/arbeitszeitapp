from dataclasses import dataclass

from arbeitszeit.interactors import query_private_consumptions as interactor
from arbeitszeit_web.session import Session, UserRole


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class QueryPrivateConsumptionsController:
    session: Session

    def process_request(self) -> interactor.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        match self.session.get_user_role():
            case UserRole.member:
                return interactor.Request(member=user_id)
        return InvalidRequest(status_code=403)
