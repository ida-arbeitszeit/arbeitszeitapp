from dataclasses import dataclass


@dataclass
class Request:
    email_address: str
    new_password: str


@dataclass
class Response:
    is_changed: bool


@dataclass
class ChangeUserPasswordUseCase:
    def change_user_password(self, request: Request) -> Response:
        raise NotImplementedError("not yet implemented")
