from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class GetAccountantDashboardUseCase:
    @dataclass
    class Response:
        accountant_id: UUID
        name: str
        email: str

    class Failure(Exception):
        pass

    database: DatabaseGateway

    def get_dashboard(self, user: UUID) -> Response:
        accountant = self.database.get_accountants().with_id(user).first()
        if not accountant:
            raise self.Failure()
        return self.Response(
            accountant_id=user, name=accountant.name, email=accountant.email_address
        )
