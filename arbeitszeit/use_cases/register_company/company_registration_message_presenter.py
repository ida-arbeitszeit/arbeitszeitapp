from typing import Protocol
from uuid import UUID


class CompanyRegistrationMessagePresenter(Protocol):
    def show_company_registration_message(self, company: UUID, token: str) -> None:
        ...
