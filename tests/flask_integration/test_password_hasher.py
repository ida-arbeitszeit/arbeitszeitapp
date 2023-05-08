from arbeitszeit_flask.password_hasher import PasswordHasherImpl

from .flask import FlaskTestCase


class PasswordHasherTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.password_hasher = self.injector.get(PasswordHasherImpl)

    def test_that_previously_hashed_password_matches_its_hash(self) -> None:
        password = "test 123 password"
        hashed = self.password_hasher.calculate_password_hash(password)
        assert self.password_hasher.is_password_matching_hash(
            password=password, password_hash=hashed
        )

    def test_random_string_does_not_match_hashed_password(self) -> None:
        hashed = self.password_hasher.calculate_password_hash("the password 123")
        assert not self.password_hasher.is_password_matching_hash(
            password="random string", password_hash=hashed
        )
