from functools import wraps
from logging import getLogger
from typing import Callable, TypeVar

import click
from flask_babel import force_locale

from arbeitszeit.use_cases.calculate_fic_and_update_expired_plans import (
    CalculateFicAndUpdateExpiredPlans,
)
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection

LOGGER = getLogger(__name__)
CallableT = TypeVar("CallableT", bound=Callable)


@commit_changes
@with_injection()
def calculate_fic_and_update_expired_plans(
    calculate_fic_and_update_expired_plans: CalculateFicAndUpdateExpiredPlans,
) -> None:
    calculate_fic_and_update_expired_plans()


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


def deprecated(message):
    def wrap(f: CallableT) -> CallableT:
        @wraps(f)
        def wrapper(*args, **kwargs):
            LOGGER.warning("Deprecated: %s", message)
            return f(*args, **kwargs)

        return wrapper  # type: ignore

    return wrap
