from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import AccountantRepository


@dataclass
class GetAccountantDashboardUseCase:
    @dataclass
    class Response:
        accountant_id: UUID
        name: str
        email: str

    class Failure(Exception):
        pass

    accountant_repository: AccountantRepository

    def get_dashboard(self, user: UUID) -> Response:
        accountant = self.accountant_repository.get_accountants().with_id(user).first()
        if not accountant:
            raise self.Failure()
        return self.Response(
            accountant_id=user, name=accountant.name, email=accountant.email_address
        )
