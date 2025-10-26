from uuid import uuid4

from parameterized import parameterized

from arbeitszeit import records
from tests.db.base_test_case import DatabaseTestCase

from .utility import Utility


class AccountantResultTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def create_accountant(
        self, *, email_address: str = "test@test.test", name: str = "test name"
    ) -> records.Accountant:
        self.database_gateway.create_email_address(
            address=email_address, confirmed_on=None
        )
        credentials = self.database_gateway.create_account_credentials(
            email_address=email_address,
            password_hash="1234",
        )
        return self.database_gateway.create_accountant(
            name=name,
            account_credentials=credentials.id,
        )


class CreateAccountantTests(AccountantResultTests):
    def setUp(self) -> None:
        super().setUp()
        self.expected_email = "test@test.test"
        self.expected_name = "test name"
        self.accountant = self.create_accountant(
            email_address=self.expected_email, name=self.expected_name
        )
        self.uuid = self.accountant.id

    def test_repository_stores_name_correctly(self) -> None:
        accountant = self.database_gateway.get_accountants().with_id(self.uuid).first()
        assert accountant
        self.assertEqual(accountant.name, self.expected_name)


class CreateAccountantWithExistingMemberEmailTests(AccountantResultTests):
    def setUp(self) -> None:
        super().setUp()
        self.expected_email = "test@test.test"

    def test_can_create_accountant_with_same_email_address_as_member(self) -> None:
        self.member_generator.create_member(email=self.expected_email)
        account_credentials = (
            self.database_gateway.get_account_credentials()
            .with_email_address(self.expected_email)
            .first()
        )
        assert account_credentials
        self.database_gateway.create_accountant(
            account_credentials=account_credentials.id,
            name="test name",
        )


class GetAccountantsTests(AccountantResultTests):
    def test_that_by_default_there_are_no_accountants_in_db(self) -> None:
        assert not self.database_gateway.get_accountants()

    def test_that_one_item_is_shown_after_accountant_was_created(self) -> None:
        self.create_accountant()
        assert len(self.database_gateway.get_accountants()) == 1

    def test_that_correct_name_is_retrieved(self) -> None:
        expected_name = "test name 123"
        self.create_accountant(name=expected_name)
        item = list(self.database_gateway.get_accountants())[0]
        assert item.name == expected_name


class WithIdTests(AccountantResultTests):
    def test_with_any_accountants_in_db_that_result_set_is_empty(self) -> None:
        assert not self.database_gateway.get_accountants().with_id(uuid4())

    def test_result_set_is_empty_with_with_unknown_id_and_one_accountant_in_db(
        self,
    ) -> None:
        self.create_accountant()
        assert not self.database_gateway.get_accountants().with_id(uuid4())

    def test_result_set_contains_1_entry_with_id_for_previously_created_accountant(
        self,
    ) -> None:
        accountant = self.create_accountant()
        assert len(self.database_gateway.get_accountants().with_id(accountant.id)) == 1


class WithEmailAddressTests(AccountantResultTests):
    def test_result_set_is_empty_with_empty_db(self) -> None:
        assert not self.database_gateway.get_accountants().with_email_address(
            "fake@mail.test"
        )

    def test_result_set_is_empty_with_unknown_email_address_and_one_accountant_in_db(
        self,
    ) -> None:
        self.create_accountant(email_address="test@test.test")
        assert not self.database_gateway.get_accountants().with_email_address(
            "fake@mail.test"
        )

    def test_result_set_contains_one_record_with_known_email_address_of_existing_accountant(
        self,
    ) -> None:
        expected_email_address = "test1@test.test"
        self.create_accountant(email_address=expected_email_address)
        assert (
            len(
                self.database_gateway.get_accountants().with_email_address(
                    expected_email_address
                )
            )
            == 1
        )

    def test_result_set_contains_one_record_with_case_insensitive_email_address_of_existing_accountant(
        self,
    ) -> None:
        email = "test@test.test"
        self.create_accountant(email_address=email)
        altered_email = Utility.mangle_case(email)
        assert (
            len(
                self.database_gateway.get_accountants().with_email_address(
                    altered_email
                )
            )
            == 1
        )


class JoinedWithEmailAddressTests(AccountantResultTests):
    @parameterized.expand(["test@test.test"])
    def test_that_email_address_is_the_one_that_accountant_was_created_with(
        self, expected_address
    ) -> None:
        self.create_accountant(email_address=expected_address)
        assert all(
            result[1].address == expected_address
            for result in self.database_gateway.get_accountants().joined_with_email_address()
        )

    @parameterized.expand([(0,), (1,), (2,)])
    def test_that_result_has_length_equal_to_amount_of_created_accountants(
        self, n: int
    ) -> None:
        for _ in range(n):
            self.accountant_generator.create_accountant()
        assert (
            len(self.database_gateway.get_accountants().joined_with_email_address())
            == n
        )
