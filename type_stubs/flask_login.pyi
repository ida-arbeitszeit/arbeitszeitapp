from datetime import datetime
from typing import Any, Optional, TypeVar

T = TypeVar("T")

def login_user(user, remember: bool = ...) -> None:
    pass

def logout_user() -> None:
    pass

def login_required(callable: T) -> T: ...

class CurrentUser:
    id: str
    email: str
    is_authenticated: bool
    confirmed_on: Optional[datetime]
    name: str

current_user: CurrentUser

class UserMixin: ...
class LoginManager(Any): ...
