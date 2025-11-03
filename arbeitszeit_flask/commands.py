import click
from flask_babel import force_locale

from arbeitszeit.interactors.send_accountant_registration_token import (
    SendAccountantRegistrationTokenInteractor,
)
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection


@click.argument("email_address")
@commit_changes
@with_injection()
def invite_accountant(
    email_address: str, interactor: SendAccountantRegistrationTokenInteractor
) -> None:
    """Invite an accountant by sending a registration token to the given email address."""
    with force_locale("de"):  # type: ignore
        interactor.send_accountant_registration_token(
            SendAccountantRegistrationTokenInteractor.Request(email=email_address)
        )
