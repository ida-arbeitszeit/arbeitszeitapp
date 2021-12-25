from typing import Any, TypeVar

T = TypeVar("T")

def login_user() -> None:
    pass

def logout_user() -> None:
    pass

def login_required(callable: T) -> T: ...

class CurrentUser:
    id: str
    email: str

current_user: CurrentUser

class UserMixin: ...
class LoginManager(Any): ...
