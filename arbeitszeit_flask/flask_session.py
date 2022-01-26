from typing import Optional
from uuid import UUID

from flask_login import current_user


class FlaskSession:
    def get_current_user(self) -> Optional[UUID]:
        if current_user is None:
            return None
        else:
            return UUID(current_user.id)
