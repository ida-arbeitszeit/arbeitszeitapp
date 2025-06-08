import click
from flask_babel import force_locale

from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection


@click.argument("email_address")
@commit_changes
@with_injection()
def invite_accountant(
    email_address: str, use_case: SendAccountantRegistrationTokenUseCase
) -> None:
    """Invite an accountant by sending a registration token to the given email address."""
    with force_locale("de"):  # type: ignore
        use_case.send_accountant_registration_token(
            SendAccountantRegistrationTokenUseCase.Request(email=email_address)
        )
