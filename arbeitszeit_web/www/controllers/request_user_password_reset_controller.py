from dataclasses import dataclass

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RequestUserPasswordResetController:
    database: DatabaseGateway

    def process_user_password_reset_request(self):
        raise NotImplemented("not impled")