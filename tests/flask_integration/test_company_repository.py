from datetime import datetime
from typing import List
from uuid import uuid4

from flask_sqlalchemy import SQLAlchemy
from pytest import raises
from sqlalchemy.exc import IntegrityError

from arbeitszeit.entities import Company
from arbeitszeit_flask.database.repositories import AccountRepository, CompanyRepository
from tests.data_generators import CompanyGenerator, MemberGenerator

from .flask import FlaskTestCase


def company_in_companies(company: Company, companies: List[Company]) -> bool:
    return company.id in [c.id for c in companies]


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_repository = self.injector.get(CompanyRepository)
        self.account_repository = self.injector.get(AccountRepository)

    def test_cannot_retrieve_company_from_arbitrary_uuid(self) -> None:
        assert not self.company_repository.get_companies().with_id(uuid4())

    def test_can_retrieve_a_company_by_its_uuid(self) -> None:
        company = self.company_generator.create_company_entity()
        assert (
            self.company_repository.get_companies().with_id(company.id).first()
            == company
        )

    def test_can_retrieve_a_company_by_its_email(self) -> None:
        expected_email = "expected@mail.com"
        expected_company = self.company_generator.create_company_entity(
            email=expected_email
        )
        assert (
            self.company_repository.get_companies()
            .with_email_address(expected_email)
            .first()
            == expected_company
        )

    def test_that_random_email_returns_no_company(self) -> None:
        random_email = "xyz123@testmail.com"
        self.company_generator.create_company_entity(email="test_mail@testmail.com")
        assert not self.company_repository.get_companies().with_email_address(
            random_email
        )

    def test_can_create_company_with_correct_name(self) -> None:
        means_account = self.account_repository.create_account()
        labour_account = self.account_repository.create_account()
        resource_account = self.account_repository.create_account()
        products_account = self.account_repository.create_account()
        expected_name = "Rosa"
        company = self.company_repository.create_company(
            email="rosa@cp.org",
            name=expected_name,
            password_hash="testpassword",
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resource_account,
            products_account=products_account,
            registered_on=datetime.now(),
        )
        assert company.name == expected_name

    def test_can_detect_if_company_with_email_is_already_present(self) -> None:
        expected_email = "rosa@cp.org"
        companies = self.company_repository.get_companies()
        assert not companies.with_email_address(expected_email)
        self.company_generator.create_company_entity(email=expected_email)
        assert companies.with_email_address(expected_email)

    def test_does_not_identify_random_id_with_company(self) -> None:
        company_id = uuid4()
        assert not self.company_repository.get_companies().with_id(company_id)

    def test_does_not_identify_member_as_company(self) -> None:
        member = self.member_generator.create_member()
        assert not self.company_repository.get_companies().with_id(member)

    def test_does_identify_company_id_as_company(self) -> None:
        company = self.company_generator.create_company_entity()
        assert self.company_repository.get_companies().with_id(company.id)

    def test_count_no_registered_company_if_none_was_created(self) -> None:
        assert len(self.company_repository.get_companies()) == 0

    def test_count_one_registered_company_if_one_was_created(self) -> None:
        self.company_generator.create_company_entity()
        assert len(self.company_repository.get_companies()) == 1

    def test_that_can_not_register_company_with_same_email_twice(self) -> None:
        with raises(IntegrityError):
            self.company_generator.create_company_entity(email="company@provider.de")
            self.company_generator.create_company_entity(email="company@provider.de")

    def test_that_get_all_companies_returns_all_companies(self) -> None:
        expected_company1 = self.company_generator.create_company_entity(
            email="company1@provider.de"
        )
        expected_company2 = self.company_generator.create_company_entity(
            email="company2@provider.de"
        )
        all_companies = list(self.company_repository.get_companies())
        assert company_in_companies(expected_company1, all_companies)
        assert company_in_companies(expected_company2, all_companies)


class CreateCompanyTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = self.injector.get(SQLAlchemy)
        self.repository = self.injector.get(CompanyRepository)
        self.account_repository = self.injector.get(AccountRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.means_account = self.account_repository.create_account()
        self.labour_account = self.account_repository.create_account()
        self.resource_account = self.account_repository.create_account()
        self.products_account = self.account_repository.create_account()
        self.timestamp = datetime(2000, 1, 1)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_company_can_be_created_while_member_with_same_email_exists(
        self,
    ) -> None:
        email = "test@test.test"
        self.member_generator.create_member_entity(email=email)
        self.repository.create_company(
            email=email,
            name="test name",
            password_hash="testpassword",
            means_account=self.means_account,
            labour_account=self.labour_account,
            resource_account=self.resource_account,
            products_account=self.products_account,
            registered_on=self.timestamp,
        )
        self.db.session.flush()


class ConfirmCompanyTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(CompanyRepository)
        self.account_repository = self.injector.get(AccountRepository)

    def test_that_newly_created_company_is_not_confirmed(self) -> None:
        company = self._create_company()
        self.assertFalse(self.repository.is_company_confirmed(company.id))

    def test_that_company_is_confirmed_after_confirm_was_called(self) -> None:
        company = self._create_company()
        self.repository.confirm_company(company.id, datetime(2000, 1, 2))
        self.assertTrue(self.repository.is_company_confirmed(company.id))

    def test_when_confirming_company_other_company_stays_unconfirmed(self) -> None:
        company = self._create_company()
        other_company = self._create_company("other@company.org")
        self.repository.confirm_company(company.id, datetime(2000, 1, 2))
        self.assertFalse(self.repository.is_company_confirmed(other_company.id))

    def test_non_existing_company_counts_as_unconfirmed(self) -> None:
        self.assertFalse(self.repository.is_company_confirmed(company=uuid4()))

    def _create_company(self, email: str = "test@test.test") -> Company:
        means_account = self.account_repository.create_account()
        labour_account = self.account_repository.create_account()
        resource_account = self.account_repository.create_account()
        products_account = self.account_repository.create_account()
        return self.repository.create_company(
            email=email,
            name="test name",
            password_hash="some password",
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resource_account,
            products_account=products_account,
            registered_on=datetime(2000, 1, 1),
        )


class ThatAreWorkplaceOfMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(CompanyRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_by_default_random_members_are_not_assigned_to_a_company(self) -> None:
        self.company_generator.create_company()
        member = self.member_generator.create_member()
        assert not self.repository.get_companies().that_are_workplace_of_member(member)

    def test_that_companies_are_retrieved_if_member_is_explict_worker_at_company(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.company_generator.create_company(workers=[member])
        assert self.repository.get_companies().that_are_workplace_of_member(member)

    def test_that_workplace_is_returned_after_one_is_registered(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()
        self.repository.get_companies().with_id(company).add_worker(member)
        assert (
            self.repository.get_companies()
            .that_are_workplace_of_member(member)
            .with_id(company)
        )


class WithNameContainingTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(CompanyRepository)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_companies_can_be_filtered_by_name(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.repository.get_companies().with_name_containing("abc123")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_subset_of_name(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.repository.get_companies().with_name_containing("bc1")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_subset_of_name_regardless_of_case(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.repository.get_companies().with_name_containing("bC1")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id


class WithEmailContainingTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(CompanyRepository)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_companies_can_be_filtered_by_email(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_company = list(
            self.repository.get_companies().with_email_containing("some.mail@cp.org")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_substring_of_email(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_company = list(
            self.repository.get_companies().with_email_containing("ail@cp")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_regardless_of_case(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_company = list(
            self.repository.get_companies().with_email_containing("aIL@cp")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id
