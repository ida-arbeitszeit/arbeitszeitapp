from uuid import uuid4

from parameterized import parameterized

from arbeitszeit import records
from tests.db.base_test_case import DatabaseTestCase


class AccountCredentialsResultTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def create_account_credentials(
        self, *, email_address: str = "test@cp.org", password_hash: str = ""
    ) -> records.AccountCredentials:
        self.database_gateway.create_email_address(
            address=email_address, confirmed_on=None
        )
        return self.database_gateway.create_account_credentials(
            email_address=email_address, password_hash=password_hash
        )

    def create_members(self, *, n: int) -> None:
        for _ in range(n):
            self.member_generator.create_member()

    def create_accountants(self, *, n: int) -> None:
        for _ in range(n):
            self.accountant_generator.create_accountant()

    def create_companies(self, *, n: int) -> None:
        for _ in range(n):
            self.company_generator.create_company()


class CreateAccountCredentialsTests(AccountCredentialsResultTests):
    @parameterized.expand(["test@test.test", "", "ABC@123.fg"])
    def test_account_credentials_created_has_correct_email_address_set(
        self, expected_email_address: str
    ) -> None:
        credentials = self.create_account_credentials(
            email_address=expected_email_address
        )
        assert credentials.email_address == expected_email_address

    @parameterized.expand(["abc", "\n\t", ""])
    def test_account_credentials_created_has_correct_password_hash_set(
        self, expected_password_hash: str
    ) -> None:
        credentials = self.create_account_credentials(
            password_hash=expected_password_hash
        )
        assert credentials.password_hash == expected_password_hash

    @parameterized.expand(["test@test.test", "", "ABC@123.fg"])
    def test_account_credentials_retrieved_from_db_have_original_email_address(
        self, expected_email_address: str
    ) -> None:
        self.create_account_credentials(email_address=expected_email_address)
        credentials = self.database_gateway.get_account_credentials().first()
        assert credentials
        assert credentials.email_address == expected_email_address

    @parameterized.expand(["abc", "\n\t", ""])
    def test_account_credentials_retrieved_from_db_have_original_password_hash(
        self, expected_password_hash: str
    ) -> None:
        self.create_account_credentials(password_hash=expected_password_hash)
        credentials = self.database_gateway.get_account_credentials().first()
        assert credentials
        assert credentials.password_hash == expected_password_hash


class JoinedWithEmailAddressAndCompanyTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_companies_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(
                self.database_gateway.get_account_credentials().joined_with_email_address_and_company()
            )
            == companies + members + accountants
        )

    @parameterized.expand(["name1", "test name 2"])
    def test_that_companies_yielded_have_their_correct_name(
        self, expected_name: str
    ) -> None:
        self.company_generator.create_company(name=expected_name)
        assert all(
            result[2] is not None and result[2].name == expected_name
            for result in self.database_gateway.get_account_credentials().joined_with_email_address_and_company()
        )


class JoinedWithEmailAddressAndMemberTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_members_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(
                self.database_gateway.get_account_credentials().joined_with_email_address_and_member()
            )
            == companies + members + accountants
        )

    @parameterized.expand(["name1", "test name 2"])
    def test_that_companies_yielded_have_their_correct_name(
        self, expected_name: str
    ) -> None:
        self.member_generator.create_member(name=expected_name)
        assert all(
            result[2] is not None and result[2].name == expected_name
            for result in self.database_gateway.get_account_credentials().joined_with_email_address_and_member()
        )


class JoinedWithEmailAddressAndAccountantTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_accountants_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(
                self.database_gateway.get_account_credentials().joined_with_email_address_and_accountant()
            )
            == companies + members + accountants
        )

    @parameterized.expand(["name1", "test name 2"])
    def test_that_companies_yielded_have_their_correct_name(
        self, expected_name: str
    ) -> None:
        self.accountant_generator.create_accountant(name=expected_name)
        assert all(
            result[2] is not None and result[2].name == expected_name
            for result in self.database_gateway.get_account_credentials().joined_with_email_address_and_accountant()
        )


class JoinedWithAccountantTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_accountants_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(
                self.database_gateway.get_account_credentials().joined_with_accountant()
            )
            == companies + members + accountants
        )

    def test_that_credentials_with_accountant_return_accountant_in_result_set(
        self,
    ) -> None:
        self.accountant_generator.create_accountant()
        assert all(
            result[1] is not None
            for result in self.database_gateway.get_account_credentials().joined_with_accountant()
        )


class JoinedWithMemberTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_members_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(self.database_gateway.get_account_credentials().joined_with_member())
            == companies + members + accountants
        )

    def test_that_credentials_with_member_return_member_in_result_set(self) -> None:
        self.member_generator.create_member()
        assert all(
            result[1] is not None
            for result in self.database_gateway.get_account_credentials().joined_with_member()
        )


class JoinedWithCompanyTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (2, 2, 2),
        ]
    )
    def test_that_credentials_without_companies_are_also_included_in_result_set(
        self, companies: int, members: int, accountants: int
    ) -> None:
        self.create_companies(n=companies)
        self.create_members(n=members)
        self.create_accountants(n=accountants)
        assert (
            len(self.database_gateway.get_account_credentials().joined_with_company())
            == companies + members + accountants
        )

    def test_that_credentials_with_company_return_company_in_result_set(self) -> None:
        self.company_generator.create_company()
        assert all(
            result[1] is not None
            for result in self.database_gateway.get_account_credentials().joined_with_company()
        )


class WithEmailAddressTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            "test@test.test",
            "TEST@TEST.TEST",
        ]
    )
    def test_that_filtering_ignores_casing(self, address: str) -> None:
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        self.database_gateway.create_account_credentials(
            email_address=address, password_hash=""
        )
        assert self.database_gateway.get_account_credentials().with_email_address(
            address
        )
        assert self.database_gateway.get_account_credentials().with_email_address(
            address.lower()
        )
        assert self.database_gateway.get_account_credentials().with_email_address(
            address.upper()
        )

    @parameterized.expand(
        [
            ("test@test.test", "test@test.test1"),
            ("TEST@TEST.TEST", ""),
            ("test@test.test", "test@test.tes"),
        ]
    )
    def test_that_emails_that_dont_match_are_filtered(
        self, address: str, filter_text: str
    ) -> None:
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        self.database_gateway.create_account_credentials(
            email_address=address, password_hash=""
        )
        assert not self.database_gateway.get_account_credentials().with_email_address(
            filter_text
        )


class ForUserAccountWithIdTests(AccountCredentialsResultTests):
    def test_that_result_includes_credentials_for_matching_member(self) -> None:
        member = self.member_generator.create_member()
        assert self.database_gateway.get_account_credentials().for_user_account_with_id(
            member
        )

    def test_that_result_includes_credentials_for_matching_accountant(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        assert self.database_gateway.get_account_credentials().for_user_account_with_id(
            accountant
        )

    def test_that_result_includes_credentials_for_matching_company(self) -> None:
        company = self.company_generator.create_company()
        assert self.database_gateway.get_account_credentials().for_user_account_with_id(
            company
        )

    def test_that_when_filtering_for_random_user_id_no_results_are_returned(
        self,
    ) -> None:
        self.member_generator.create_member()
        self.company_generator.create_company()
        self.accountant_generator.create_accountant()
        assert not self.database_gateway.get_account_credentials().for_user_account_with_id(
            uuid4()
        )


class UpdateTests(AccountCredentialsResultTests):
    @parameterized.expand(
        [
            ("old@test.test", "new@test.test"),
            ("old@test.test", "new2@test.test"),
        ]
    )
    def test_can_query_for_new_mail_address_after_adress_update(
        self, old_email_address: str, new_email_address: str
    ) -> None:
        self.member_generator.create_member(email=old_email_address)
        assert not self.database_gateway.get_account_credentials().with_email_address(
            new_email_address
        )
        self.database_gateway.create_email_address(
            address=new_email_address, confirmed_on=None
        )
        self.database_gateway.get_account_credentials().update().change_email_address(
            new_email_address
        ).perform()
        assert self.database_gateway.get_account_credentials().with_email_address(
            new_email_address
        )

    def test_that_0_rows_are_affected_when_update_is_performed_on_empty_set(
        self,
    ) -> None:
        self.database_gateway.create_email_address(
            address="test@test.test", confirmed_on=None
        )
        rows_affected = (
            self.database_gateway.get_account_credentials()
            .update()
            .change_email_address("test@test.test")
            .perform()
        )
        assert not rows_affected

    def test_that_1_row_is_affected_when_update_is_performed_on_query_matching_a_single_user(
        self,
    ) -> None:
        self.member_generator.create_member()
        self.database_gateway.create_email_address(
            address="test@test.test", confirmed_on=None
        )
        rows_affected = (
            self.database_gateway.get_account_credentials()
            .update()
            .change_email_address("test@test.test")
            .perform()
        )
        assert rows_affected == 1

    def test_that_0_rows_are_affected_when_updated_performed_is_empty(
        self,
    ) -> None:
        self.member_generator.create_member()
        self.database_gateway.create_email_address(
            address="test@test.test", confirmed_on=None
        )
        rows_affected = (
            self.database_gateway.get_account_credentials().update().perform()
        )
        assert rows_affected == 0

    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_changing_every_users_password_hash_affected_all_previously_created_users(
        self, number_of_users_created: int
    ) -> None:
        self.create_members(n=number_of_users_created)
        rows_affected = (
            self.database_gateway.get_account_credentials()
            .update()
            .change_password_hash("new hash")
            .perform()
        )
        assert rows_affected == number_of_users_created

    @parameterized.expand(
        [
            ("new_hash",),
            ("another example hash",),
        ]
    )
    def test_that_password_hash_is_updated_after_password_hash_updated_was_performed(
        self, new_hash: str
    ) -> None:
        member = self.member_generator.create_member()
        (
            self.database_gateway.get_account_credentials()
            .for_user_account_with_id(member)
            .update()
            .change_password_hash(new_hash)
            .perform()
        )
        updated_credentials = (
            self.database_gateway.get_account_credentials()
            .for_user_account_with_id(member)
            .first()
        )
        assert updated_credentials
        assert updated_credentials.password_hash == new_hash

    def test_that_changing_one_users_password_hash_does_not_affect_another_users_credentials(
        self,
    ) -> None:
        new_hash = "test hash 123"
        member_to_change = self.member_generator.create_member()
        control_member = self.member_generator.create_member()
        (
            self.database_gateway.get_account_credentials()
            .for_user_account_with_id(member_to_change)
            .update()
            .change_password_hash(new_hash)
            .perform()
        )
        control_credentials = (
            self.database_gateway.get_account_credentials()
            .for_user_account_with_id(control_member)
            .first()
        )
        assert control_credentials
        assert control_credentials.password_hash != new_hash
