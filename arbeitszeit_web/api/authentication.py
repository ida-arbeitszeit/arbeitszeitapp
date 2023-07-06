from dataclasses import dataclass

from arbeitszeit_web.api.response_errors import Unauthorized
from arbeitszeit_web.session import Session


@dataclass
class Authenticator:
    session: Session

    def authenticate_request(self) -> None:
        user_id = self.session.get_current_user()
        if user_id is None:
            raise Unauthorized(
                message="You have to authenticate before using this service."
            )
