from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from tests.data_generators import MemberGenerator

from ..flask import FlaskTestCase

from .utility import Utility


class CreateAccountantTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.expected_email = "test@test.test"
        self.expected_name = "test name"
        self.expected_password = "test password"
        self.uuid = self.database_gateway.create_accountant(
            email=self.expected_email,
            name=self.expected_name,
            password_hash=self.expected_password,
        )

    def test_repository_stores_email_address_correctly(self) -> None:
        accountant = self.database_gateway.get_accountants().with_id(self.uuid).first()
        assert accountant
        self.assertEqual(accountant.email_address, self.expected_email)

    def test_repository_stores_name_correctly(self) -> None:
        accountant = self.database_gateway.get_accountants().with_id(self.uuid).first()
        assert accountant
        self.assertEqual(accountant.name, self.expected_name)

    def test_cannot_create_accountant_with_same_email_twice(self) -> None:
        with self.assertRaises(IntegrityError):
            self.uuid = self.database_gateway.create_accountant(
                email=self.expected_email,
                name=self.expected_name,
                password_hash=self.expected_password,
            )
            self.db.session.flush()

    def test_cannot_create_accountant_with_similar_email_case_insensitive(self) -> None:
        with self.assertRaises(IntegrityError):
            altered_email = Utility.mangle_case(self.expected_email)
            self.uuid = self.database_gateway.create_accountant(
                email=altered_email,
                name=self.expected_name,
                password_hash=self.expected_password,
            )
            self.db.session.flush()



class CreateAccountantWithExistingMemberEmailTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = self.injector.get(SQLAlchemy)
        self.member_generator = self.injector.get(MemberGenerator)
        self.expected_email = "test@test.test"
        self.expected_name = "test name"
        self.expected_password = "test password"

    def test_can_create_accountant_with_same_email_address_as_member(self) -> None:
        self.member_generator.create_member_entity(email=self.expected_email)
        self.database_gateway.create_accountant(
            email=self.expected_email,
            name=self.expected_name,
            password_hash=self.expected_password,
        )
        self.db.session.flush()

    def test_can_create_accountant_with_similar_email_address_as_member_case_insensitive(
        self,
    ) -> None:
        self.member_generator.create_member_entity(email=self.expected_email)
        altered_email = Utility.mangle_case(self.expected_email)
        new_accountant_id = self.database_gateway.create_accountant(
            email=altered_email,
            name=self.expected_name,
            password_hash=self.expected_password,
        )
        self.db.session.flush()
        new_accountant = self.database_gateway.get_accountants().with_id(new_accountant_id).first()
        self.db.session.flush()
        assert new_accountant.email_address == self.expected_email

class ValidationTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.expected_email = "test@test.test"
        self.expected_password = "test password"
        self.uuid = self.database_gateway.create_accountant(
            email=self.expected_email,
            name="test name",
            password_hash=self.expected_password,
        )


class GetAccountantsTests(FlaskTestCase):
    def test_that_by_default_there_are_no_accountants_in_db(self) -> None:
        assert not self.database_gateway.get_accountants()

    def test_that_one_item_is_shown_after_accountant_was_created(self) -> None:
        self.database_gateway.create_accountant(
            email="test@test.test", name="test accountant", password_hash="1234"
        )
        assert len(self.database_gateway.get_accountants()) == 1

    def test_that_correct_email_address_is_retrieved(self) -> None:
        expected_email_address = "test@email.com"
        self.database_gateway.create_accountant(
            email=expected_email_address, name="test accountant", password_hash="1234"
        )
        item = list(self.database_gateway.get_accountants())[0]
        assert item.email_address == expected_email_address

    def test_that_correct_name_is_retrieved(self) -> None:
        expected_name = "test name 123"
        self.database_gateway.create_accountant(
            email="test@test.test", name=expected_name, password_hash="1234"
        )
        item = list(self.database_gateway.get_accountants())[0]
        assert item.name == expected_name


class WithIdTests(FlaskTestCase):
    def test_with_any_accountants_in_db_that_result_set_is_empty(self) -> None:
        assert not self.database_gateway.get_accountants().with_id(uuid4())

    def test_result_set_is_empty_with_with_unknown_id_and_one_accountant_in_db(
        self,
    ) -> None:
        self.database_gateway.create_accountant(
            email="test@test.test", name="test name", password_hash="1234"
        )
        assert not self.database_gateway.get_accountants().with_id(uuid4())

    def test_result_set_contains_1_entry_with_id_for_previously_created_accountant(
        self,
    ) -> None:
        accountant_id = self.database_gateway.create_accountant(
            email="test@test.test", name="test name", password_hash="1234"
        )
        assert len(self.database_gateway.get_accountants().with_id(accountant_id)) == 1


class WithEmailAddressTests(FlaskTestCase):
    def test_result_set_is_empty_with_empty_db(self) -> None:
        assert not self.database_gateway.get_accountants().with_email_address(
            "fake@mail.test"
        )

    def test_result_set_is_empty_with_unknown_email_address_and_one_accountant_in_db(
        self,
    ) -> None:
        self.database_gateway.create_accountant(
            email="test@test.test", name="test name", password_hash="1234"
        )
        assert not self.database_gateway.get_accountants().with_email_address(
            "fake@mail.test"
        )

    def test_result_set_contains_one_record_with_known_email_address_of_existing_accountant(
        self,
    ) -> None:
        self.database_gateway.create_accountant(
            email="test@test.test", name="test name", password_hash="1234"
        )
        assert (
            len(
                self.database_gateway.get_accountants().with_email_address(
                    "test@test.test"
                )
            )
            == 1
        )

    def test_result_set_contains_one_record_with_case_insensitive_email_address_of_existing_accountant(
        self,
    ) -> None:
        email = "test@test.test"
        self.database_gateway.create_accountant(
            email=email, name="test name", password_hash="1234"
        )
        altered_email = Utility.mangle_case(email)
        assert (
            len(
                self.database_gateway.get_accountants().with_email_address(
                    altered_email
                )
            )
            == 1
        )

