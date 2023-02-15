from arbeitszeit_flask.commands import update_and_payout

from .flask import FlaskTestCase


class PayoutTests(FlaskTestCase):
    def test_can_run_payout_command_without_crashing(self) -> None:
        update_and_payout()
