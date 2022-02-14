from typing import Optional
from uuid import UUID

from flask_login import current_user


class FlaskSession:
    def get_current_user(self) -> Optional[UUID]:
        try:
            return UUID(current_user.id)
        except AttributeError:
            return None
