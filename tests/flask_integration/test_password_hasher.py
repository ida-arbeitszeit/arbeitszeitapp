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

    def test_that_sha256_hashes_are_considered_to_need_regeneration(self) -> None:
        example_hash = "sha256$TKh78RuuHtoNJyrk$75b108cb18648faebd476eee401441b5b62d81eee855631d209503f393e1440e"
        assert self.password_hasher.is_regeneration_needed(example_hash)

    def test_that_scrypt_hashes_are_not_considered_to_need_regeneration(self) -> None:
        example_hash = "pbkdf2:sha256:600000$XUBVbwrkdN0vFmG0$52c0b0c95101315e5167f7219487beb890c5b1d4dfa9af33015815eb4f945568"
        assert not self.password_hasher.is_regeneration_needed(example_hash)

    def test_that_hashes_generated_by_the_password_hasher_are_not_considered_to_be_in_need_of_regeneration(
        self,
    ) -> None:
        example_hash = self.password_hasher.calculate_password_hash("test123")
        assert not self.password_hasher.is_regeneration_needed(example_hash)
