from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.review_registered_consumptions import (
    ReviewRegisteredConsumptionsUseCase,
)
from arbeitszeit_web.session import Session, UserRole


@dataclass
class ReviewRegisteredConsumptionsController:
    session: Session

    def create_use_case_request(
        self,
    ) -> Optional[ReviewRegisteredConsumptionsUseCase.Request]:
        user_role = self.session.get_user_role()
        if user_role != UserRole.company:
            return None
        providing_company = self.session.get_current_user()
        if not providing_company:
            return None
        return ReviewRegisteredConsumptionsUseCase.Request(
            providing_company=providing_company
        )
