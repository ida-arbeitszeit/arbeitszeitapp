import subprocess

import click
from flask_babel import force_locale

from arbeitszeit.use_cases import UpdatePlansAndPayout
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection


@commit_changes
@with_injection()
def update_and_payout(
    payout: UpdatePlansAndPayout,
) -> None:
    """
    Run every hour on production server or call manually from CLI `flask payout`.
    """
    payout()


@click.argument("email_address")
@commit_changes
@with_injection()
def invite_accountant(
    email_address: str, use_case: SendAccountantRegistrationTokenUseCase
) -> None:
    with force_locale("de"):
        use_case.send_accountant_registration_token(
            SendAccountantRegistrationTokenUseCase.Request(email=email_address)
        )


def trans_update():
    """
    Parse code and update language specific .po-files.
    """
    subprocess.run(
        [
            "pybabel",
            "extract",
            "-F",
            "babel.cfg",
            "-k",
            "lazy_gettext",
            "-o",
            "arbeitszeit_flask/translations/messages.pot",
            ".",
        ],
        check=True,
    )
    subprocess.run(
        [
            "pybabel",
            "update",
            "-i",
            "arbeitszeit_flask/translations/messages.pot",
            "-d",
            "arbeitszeit_flask/translations",
            "--no-fuzzy-matching",
        ],
        check=True,
    )


def trans_compile():
    """Compile translation files."""
    subprocess.run(
        ["pybabel", "compile", "-d", "arbeitszeit_flask/translations"], check=True
    )


def trans_new(lang_code: str):
    """
    Add a new language.
    Examples for argument lang_code are en, de, fr, etc.
    """
    subprocess.run(
        [
            "pybabel",
            "init",
            "-i",
            "arbeitszeit_flask/translations/messages.pot",
            "-d",
            "arbeitszeit_flask/translations",
            "-l",
            lang_code,
        ],
        check=True,
    )
