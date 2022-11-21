from datetime import datetime
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from arbeitszeit.entities import AccountTypes
from arbeitszeit_flask.database.repositories import AccountRepository, MemberRepository
from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test
from .flask import FlaskTestCase


@injection_test
def test_that_users_can_be_converted_from_and_to_orm_objects(
    member_repository: MemberRepository, account_repository: AccountRepository
):
    account = account_repository.create_account(AccountTypes.member)
    expected_member = member_repository.create_member(
        email="member@cp.org",
        name="karl",
        password="password",
        account=account,
        registered_on=datetime.now(),
    )
    converted_member = member_repository.object_from_orm(
        member_repository.object_to_orm(
            expected_member,
        )
    )
    assert converted_member == expected_member


@injection_test
def test_that_member_can_be_retrieved_by_its_id(
    repository: MemberRepository,
    member_generator: MemberGenerator,
):
    expected_member = member_generator.create_member()
    retrieved_member = repository.get_members().with_id(expected_member).first()
    assert retrieved_member
    assert retrieved_member.id == expected_member


@injection_test
def test_that_member_can_be_retrieved_by_its_email(
    repository: MemberRepository, member_generator: MemberGenerator
):
    expected_mail = "test_mail@testmail.com"
    expected_member = member_generator.create_member_entity(email=expected_mail)
    assert (
        repository.get_members().with_email_address(expected_mail).first()
        == expected_member
    )


@injection_test
def test_that_random_email_returns_no_member(
    repository: MemberRepository, member_generator: MemberGenerator
):
    random_email = "xyz123@testmail.com"
    member_generator.create_member_entity(email="test_mail@testmail.com")
    assert not repository.get_members().with_email_address(random_email)


@injection_test
def test_cannot_find_member_by_email_before_it_was_added(
    member_repository: MemberRepository,
    account_repository: AccountRepository,
):
    members = member_repository.get_members()
    assert not members.with_email_address("member@cp.org")
    account = account_repository.create_account(AccountTypes.member)
    member_repository.create_member(
        email="member@cp.org",
        name="karl",
        password="password",
        account=account,
        registered_on=datetime.now(),
    )
    assert members.with_email_address("member@cp.org")


@injection_test
def test_does_not_identify_random_id_with_member(member_repository: MemberRepository):
    member_id = uuid4()
    assert not member_repository.get_members().with_id(member_id)


@injection_test
def test_does_not_identify_company_as_member(
    company_generator: CompanyGenerator, member_repository: MemberRepository
):
    company = company_generator.create_company_entity()
    assert not member_repository.get_members().with_id(company.id)


@injection_test
def test_does_identify_member_id_as_member(
    member_repository: MemberRepository,
    account_repository: AccountRepository,
):
    account = account_repository.create_account(AccountTypes.member)
    member = member_repository.create_member(
        email="member@cp.org",
        name="karl",
        password="password",
        account=account,
        registered_on=datetime.now(),
    )
    assert member_repository.get_members().with_id(member.id)


@injection_test
def test_member_count_is_0_when_none_were_created(
    repository: MemberRepository,
) -> None:
    assert len(repository.get_members()) == 0


@injection_test
def test_count_one_registered_member_when_one_was_created(
    generator: MemberGenerator,
    repository: MemberRepository,
) -> None:
    generator.create_member_entity()
    assert len(repository.get_members()) == 1


@injection_test
def test_with_id_returns_no_members_when_member_does_not_exist(
    repository: MemberRepository,
) -> None:
    assert not repository.get_members().with_id(uuid4())


class GetAllMembersTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.repository = self.injector.get(MemberRepository)

    def test_with_empty_db_the_first_member_is_none(self) -> None:
        assert self.repository.get_members().first() is None

    def test_with_one_member_id_db_the_first_element_is_that_member(self) -> None:
        expected_member_id = self.member_generator.create_member()
        member = self.repository.get_members().first()
        assert member
        assert member.id == expected_member_id

    def test_that_all_members_can_be_retrieved(self) -> None:
        expected_member1 = self.member_generator.create_member_entity()
        expected_member2 = self.member_generator.create_member_entity()
        all_members = list(self.repository.get_members())
        assert expected_member1 in all_members
        assert expected_member2 in all_members

    def test_that_number_of_returned_members_is_equal_to_number_of_created_members(
        self,
    ) -> None:
        expected_number_of_members = 3
        for i in range(expected_number_of_members):
            self.member_generator.create_member_entity()
        member_count = len(self.repository.get_members())
        assert member_count == expected_number_of_members

    def test_can_filter_members_by_their_workplace(self) -> None:
        member = self.member_generator.create_member()
        self.member_generator.create_member()
        company = self.company_generator.create_company_entity(workers=[member])
        assert len(self.repository.get_members()) == 2
        assert len(self.repository.get_members().working_at_company(company.id)) == 1


class ValidateCredentialTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(MemberRepository)
        self.account_repository = self.injector.get(AccountRepository)
        self.account = self.account_repository.create_account(
            account_type=AccountTypes.member
        )
        self.timestamp = datetime(2000, 1, 1)

    def test_correct_email_and_password_can_be_validated(self) -> None:
        expected_email = "test@test.test"
        password = "test password"
        self.repository.create_member(
            email=expected_email,
            name="test",
            password=password,
            account=self.account,
            registered_on=self.timestamp,
        )
        self.assertTrue(
            self.repository.validate_credentials(
                email=expected_email, password=password
            )
        )

    def test_correct_member_id_is_returned(self) -> None:
        expected_email = "test@test.test"
        password = "test password"
        member = self.repository.create_member(
            email=expected_email,
            name="test",
            password=password,
            account=self.account,
            registered_on=self.timestamp,
        )
        self.assertEqual(
            self.repository.validate_credentials(
                email=expected_email, password=password
            ),
            member.id,
        )

    def test_cannot_validate_with_wrong_password(self) -> None:
        expected_email = "test@test.test"
        self.repository.create_member(
            email=expected_email,
            name="test",
            password="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        self.assertFalse(
            self.repository.validate_credentials(
                email=expected_email,
                password="other password",
            )
        )

    def test_cannot_validate_with_wrong_email(self) -> None:
        password = "test password"
        self.repository.create_member(
            email="test@test.test",
            name="test",
            password=password,
            account=self.account,
            registered_on=self.timestamp,
        )
        self.assertFalse(
            self.repository.validate_credentials(
                email="other@email.test",
                password=password,
            )
        )

    def test_that_validation_fails_with_no_members_in_db(self) -> None:
        self.assertFalse(
            self.repository.validate_credentials(
                email="test@test.test", password="test"
            )
        )


class ConfirmMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(MemberRepository)
        self.account_repository = self.injector.get(AccountRepository)
        self.account = self.account_repository.create_account(
            account_type=AccountTypes.member
        )
        self.timestamp = datetime(2000, 1, 1)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_confirmed_on_gets_updated_for_affected_user(self) -> None:
        expected_timestamp = datetime(2000, 1, 2)
        member_id = self.create_member()
        self.repository.get_members().with_id(member_id).set_confirmation_timestamp(
            expected_timestamp
        )
        member = self.repository.get_members().with_id(member_id).first()
        assert member
        assert member.confirmed_on == expected_timestamp

    def test_that_member_is_confirmed_after_confirmation_date_is_set(self) -> None:
        member_id = self.create_member()
        self.repository.get_members().with_id(member_id).set_confirmation_timestamp(
            datetime(2000, 1, 2)
        )
        assert self.repository.get_members().with_id(member_id).that_are_confirmed()

    def test_that_member_is_not_confirmed_before_setting_confirmation_date(
        self,
    ) -> None:
        member_id = self.create_member()
        assert not self.repository.get_members().that_are_confirmed().with_id(member_id)

    def test_that_confirmed_on_does_not_get_updated_for_other_user(self) -> None:
        other_member_id = self.member_generator.create_member_entity(confirmed=False).id
        expected_timestamp = datetime(2000, 1, 2)
        member_id = self.create_member()
        self.repository.get_members().with_id(member_id).set_confirmation_timestamp(
            expected_timestamp
        )
        member = self.repository.get_members().with_id(other_member_id).first()
        assert member
        assert member.confirmed_on is None

    def test_that_member_confirmation_returns_the_count_of_update_members(self) -> None:
        expected_count = 5
        for _ in range(5):
            self.member_generator.create_member_entity()
        print(list(self.repository.get_members()))
        assert (
            expected_count
            == self.repository.get_members().set_confirmation_timestamp(
                datetime(2000, 1, 1)
            )
        )

    def create_member(self) -> UUID:
        member = self.repository.create_member(
            email="test email",
            name="test name",
            password="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        return member.id


class CreateMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(MemberRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)
        self.account_repository = self.injector.get(AccountRepository)
        self.account = self.account_repository.create_account(
            account_type=AccountTypes.member
        )
        self.timestamp = datetime(2000, 1, 1)
        self.db = self.injector.get(SQLAlchemy)

    def test_can_create_member_with_same_email_as_company(self) -> None:
        email = "test@test.test"
        self.company_generator.create_company_entity(email=email)
        self.repository.create_member(
            email=email,
            name="test name",
            password="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        self.db.session.flush()

    def test_cannot_create_member_with_same_email_twice(self) -> None:
        email = "test@test.test"
        self.repository.create_member(
            email=email,
            name="test name",
            password="test password",
            account=self.account,
            registered_on=self.timestamp,
        )
        with self.assertRaises(IntegrityError):
            self.repository.create_member(
                email=email,
                name="test name",
                password="test password",
                account=self.account,
                registered_on=self.timestamp,
            )
            self.db.session.flush()
