from datetime import datetime
from typing import Any, Optional, TypeVar

T = TypeVar("T")

def login_user(user, remember: bool = ...) -> None:
    pass

def logout_user() -> None:
    pass

def login_required(callable: T) -> T: ...

class User:
    email: str
    email_confirmed_on: Optional[datetime]

class CurrentUser:
    id: str
    user: User
    is_authenticated: bool
    name: str

current_user: CurrentUser

class UserMixin: ...
class LoginManager(Any): ...
