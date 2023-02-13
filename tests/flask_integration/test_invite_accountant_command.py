from arbeitszeit_flask.commands import invite_accountant

from .flask import FlaskTestCase


class InviteAccountantTests(FlaskTestCase):
    def test_can_invite_accountant_without_crashing(self) -> None:
        invite_accountant("test@test.test")
