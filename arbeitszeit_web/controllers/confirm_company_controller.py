from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase as UseCase
from arbeitszeit_web.token import TokenService


@dataclass
class ConfirmCompanyController:
    token_service: TokenService

    def process_request(self, token: str) -> Optional[UseCase.Request]:
        email_address = self.token_service.confirm_token(
            token, max_age=timedelta(days=1)
        )
        if not email_address:
            return None
        return UseCase.Request(email_address=email_address)
