from dataclasses import dataclass
from datetime import timedelta

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender, ResetPasswordRequest
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    email_address: str
    reset_token: str


@dataclass
class Response:
    email_address: str


class Config:
    time_threshold_min: int = 30
    max_reset_requests: int = 5


@dataclass
class RequestUserPasswordResetUseCase:
    database: DatabaseGateway
    datetime_service: DatetimeService
    email_sender: EmailSender

    def reset_user_password(self, request: Request) -> Response:
        records = (
            self.database.get_password_reset_requests()
            .with_email_address(request.email_address)
            .with_creation_date_after(
                self.datetime_service.now()
                - timedelta(minutes=Config.time_threshold_min)
            )
        )
        if len(records) < Config.max_reset_requests:
            created_record = self.database.create_password_reset_request(
                email_address=request.email_address,
                reset_token=request.reset_token,
                created_at=self.datetime_service.now(),
            )
            self.email_sender.send_email(
                ResetPasswordRequest(
                    email_address=created_record.email_address,
                    reset_token=created_record.reset_token,
                )
            )
        return Response(email_address=request.email_address)
