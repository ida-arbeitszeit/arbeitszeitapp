from dataclasses import dataclass

from arbeitszeit.use_cases.review_registered_consumptions import (
    ReviewRegisteredConsumptionsUseCase,
)
from arbeitszeit_web.session import Session, UserRole


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class ReviewRegisteredConsumptionsController:
    session: Session

    def create_use_case_request(
        self,
    ) -> ReviewRegisteredConsumptionsUseCase.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        match self.session.get_user_role():
            case UserRole.company:
                return ReviewRegisteredConsumptionsUseCase.Request(
                    providing_company=user_id
                )
        return InvalidRequest(status_code=403)
