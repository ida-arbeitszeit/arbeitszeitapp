from datetime import datetime
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from arbeitszeit_flask.database.repositories import AccountRepository
from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator

from ..flask import FlaskTestCase


class RepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.account_repository = self.injector.get(AccountRepository)

    def test_that_member_can_be_retrieved_by_its_id(self) -> None:
        expected_member = self.member_generator.create_member()
        retrieved_member = (
            self.database_gateway.get_members().with_id(expected_member).first()
        )
        assert retrieved_member
        assert retrieved_member.id == expected_member

    def test_that_member_can_be_retrieved_by_its_email(self) -> None:
        expected_mail = "test_mail@testmail.com"
        expected_member = self.member_generator.create_member_entity(
            email=expected_mail
        )
        assert (
            self.database_gateway.get_members()
            .with_email_address(expected_mail)
            .first()
            == expected_member
        )

    def test_that_random_email_returns_no_member(self) -> None:
        random_email = "xyz123@testmail.com"
        self.member_generator.create_member_entity(email="test_mail@testmail.com")
        assert not self.database_gateway.get_members().with_email_address(random_email)

    def test_cannot_find_member_by_email_before_it_was_added(self) -> None:
        members = self.database_gateway.get_members()
        assert not members.with_email_address("member@cp.org")
        account = self.account_repository.create_account()
        self.database_gateway.create_member(
            email="member@cp.org",
            name="karl",
            password_hash="password",
            account=account,
            registered_on=datetime.now(),
        )
        assert members.with_email_address("member@cp.org")

    def test_does_not_identify_random_id_with_member(self) -> None:
        member_id = uuid4()
        assert not self.database_gateway.get_members().with_id(member_id)

    def test_does_not_identify_company_as_member(self) -> None:
        company = self.company_generator.create_company_entity()
        assert not self.database_gateway.get_members().with_id(company.id)

    def test_does_identify_member_id_as_member(self) -> None:
        account = self.account_repository.create_account()
        member = self.database_gateway.create_member(
            email="member@cp.org",
            name="karl",
            password_hash="password",
            account=account,
            registered_on=datetime.now(),
        )
        assert self.database_gateway.get_members().with_id(member.id)

    def test_member_count_is_0_when_none_were_created(self) -> None:
        assert len(self.database_gateway.get_members()) == 0

    def test_count_one_registered_member_when_one_was_created(self) -> None:
        self.member_generator.create_member_entity()
        assert len(self.database_gateway.get_members()) == 1

    def test_with_id_returns_no_members_when_member_does_not_exist(self) -> None:
        assert not self.database_gateway.get_members().with_id(uuid4())


class GetAllMembersTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_with_empty_db_the_first_member_is_none(self) -> None:
        assert self.database_gateway.get_members().first() is None

    def test_with_one_member_id_db_the_first_element_is_that_member(self) -> None:
        expected_member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().first()
        assert member
        assert member.id == expected_member_id

    def test_that_all_members_can_be_retrieved(self) -> None:
        expected_member1 = self.member_generator.create_member_entity()
        expected_member2 = self.member_generator.create_member_entity()
        all_members = list(self.database_gateway.get_members())
        assert expected_member1 in all_members
        assert expected_member2 in all_members

    def test_that_number_of_returned_members_is_equal_to_number_of_created_members(
        self,
    ) -> None:
        expected_number_of_members = 3
        for i in range(expected_number_of_members):
            self.member_generator.create_member_entity()
        member_count = len(self.database_gateway.get_members())
        assert member_count == expected_number_of_members

    def test_can_filter_members_by_their_workplace(self) -> None:
        member = self.member_generator.create_member()
        self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[member])
        assert len(self.database_gateway.get_members()) == 2
        assert (
            len(self.database_gateway.get_members().working_at_company(company.id)) == 1
        )


class ConfirmMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_repository = self.injector.get(AccountRepository)
        self.account = self.account_repository.create_account()
        self.timestamp = datetime(2000, 1, 1)

    def test_that_member_is_confirmed_after_confirmation_date_is_set(self) -> None:
        email_address = "test@test.test"
        member_id = self.create_member(email=email_address)
        self.database_gateway.get_email_addresses().with_address(
            email_address
        ).update().set_confirmation_timestamp(datetime(2000, 1, 2)).perform()
        assert (
            self.database_gateway.get_members().with_id(member_id).that_are_confirmed()
        )

    def test_that_member_is_not_confirmed_before_setting_confirmation_date(
        self,
    ) -> None:
        member_id = self.create_member()
        assert (
            not self.database_gateway.get_members()
            .that_are_confirmed()
            .with_id(member_id)
        )

    def test_that_confirmed_on_gets_updated_for_affected_user(self) -> None:
        expected_timestamp = datetime(2000, 1, 2)
        email_address = "test@test.test"
        member_id = self.create_member(email=email_address)
        self.database_gateway.get_email_addresses().with_address(
            email_address
        ).update().set_confirmation_timestamp(expected_timestamp).perform()
        record = (
            self.database_gateway.get_members()
            .with_id(member_id)
            .joined_with_email_address()
            .first()
        )
        assert record
        _, email = record
        assert email.confirmed_on == expected_timestamp

    def create_member(self, email: str = "test email") -> UUID:
        return self.database_gateway.create_member(
            email=email,
            name="test name",
            password_hash="test password",
            account=self.account,
            registered_on=self.timestamp,
        ).id


class CreateMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)
        self.account_repository = self.injector.get(AccountRepository)
        self.account = self.account_repository.create_account()
        self.timestamp = datetime(2000, 1, 1)
        self.db = self.injector.get(SQLAlchemy)

    def test_can_create_member_with_same_email_as_company(self) -> None:
        email = "test@test.test"
        self.company_generator.create_company_entity(email=email)
        self.database_gateway.create_member(
            email=email,
            name="test name",
            password_hash="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        self.db.session.flush()

    def test_cannot_create_member_with_same_email_twice(self) -> None:
        email = "test@test.test"
        self.database_gateway.create_member(
            email=email,
            name="test name",
            password_hash="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        with self.assertRaises(IntegrityError):
            self.database_gateway.create_member(
                email=email,
                name="test name",
                password_hash="test password",
                account=self.account,
                registered_on=self.timestamp,
            )
            self.db.session.flush()
