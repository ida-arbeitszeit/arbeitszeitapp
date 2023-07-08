from arbeitszeit_flask.commands import calculate_fic_and_update_expired_plans

from .flask import FlaskTestCase


class CalculateFicAndUpdateExpiredPlansCommandtests(FlaskTestCase):
    def test_can_run_command_without_crashing(self) -> None:
        calculate_fic_and_update_expired_plans()
