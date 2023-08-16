from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy

from arbeitszeit import records
from tests.data_generators import (
    CompanyGenerator,
    CooperationGenerator,
    MemberGenerator,
)

from ..flask import FlaskTestCase
from .utility import Utility


def company_in_companies(
    company: records.Company, companies: List[records.Company]
) -> bool:
    return company.id in (c.id for c in companies)


class CompanyResultTests(FlaskTestCase):
    def create_company(
        self, *, name: str = "test company name", email_address: str = "test@test.test"
    ) -> records.Company:
        self.database_gateway.create_email_address(
            address=email_address, confirmed_on=None
        )
        credentials = self.database_gateway.create_account_credentials(
            email_address=email_address, password_hash=""
        )
        return self.create_company_from_credentials(
            credentials=credentials.id, name=name
        )

    def create_company_from_credentials(
        self, credentials: UUID, *, name: str = "test@test.test"
    ) -> records.Company:
        means_account = self.database_gateway.create_account()
        labour_account = self.database_gateway.create_account()
        resource_account = self.database_gateway.create_account()
        products_account = self.database_gateway.create_account()
        return self.database_gateway.create_company(
            account_credentials=credentials,
            name=name,
            means_account=means_account,
            labour_account=labour_account,
            resource_account=resource_account,
            products_account=products_account,
            registered_on=datetime.now(),
        )


class RepositoryTester(CompanyResultTests):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_cannot_retrieve_company_from_arbitrary_uuid(self) -> None:
        assert not self.database_gateway.get_companies().with_id(uuid4())

    def test_can_retrieve_a_company_by_its_uuid(self) -> None:
        company = self.company_generator.create_company_record()
        assert (
            self.database_gateway.get_companies().with_id(company.id).first() == company
        )

    def test_can_retrieve_a_company_by_its_email(self) -> None:
        expected_email = "expected@mail.com"
        expected_company = self.company_generator.create_company_record(
            email=expected_email
        )
        assert (
            self.database_gateway.get_companies()
            .with_email_address(expected_email)
            .first()
            == expected_company
        )

    def test_can_retrieve_a_company_by_its_email_case_insensitive(
        self,
    ) -> None:
        expected_email = "expected@mail.com"
        expected_company = self.company_generator.create_company_record(
            email=expected_email
        )
        altered_email = Utility.mangle_case(expected_email)
        assert (
            self.database_gateway.get_companies()
            .with_email_address(altered_email)
            .first()
            == expected_company
        )

    def test_that_random_email_returns_no_company(self) -> None:
        random_email = "xyz123@testmail.com"
        self.company_generator.create_company_record(email="test_mail@testmail.com")
        assert not self.database_gateway.get_companies().with_email_address(
            random_email
        )

    def test_can_create_company_with_correct_name(self) -> None:
        expected_name = "Rosa"
        company = self.create_company(name=expected_name)
        assert company.name == expected_name

    def test_can_detect_if_company_with_email_is_already_present(self) -> None:
        expected_email = "rosa@cp.org"
        companies = self.database_gateway.get_companies()
        assert not companies.with_email_address(expected_email)
        self.create_company(email_address=expected_email)
        assert companies.with_email_address(expected_email)

    def test_can_detect_if_company_with_email_is_already_present_case_insensitive(
        self,
    ) -> None:
        expected_email = "rosa@cp.org"
        companies = self.database_gateway.get_companies()
        altered_email = Utility.mangle_case(expected_email)
        assert not companies.with_email_address(altered_email)
        self.company_generator.create_company_record(email=expected_email)
        assert companies.with_email_address(altered_email)

    def test_does_not_identify_random_id_with_company(self) -> None:
        company_id = uuid4()
        assert not self.database_gateway.get_companies().with_id(company_id)

    def test_does_not_identify_member_as_company(self) -> None:
        member = self.member_generator.create_member()
        assert not self.database_gateway.get_companies().with_id(member)

    def test_does_identify_company_id_as_company(self) -> None:
        company = self.company_generator.create_company_record()
        assert self.database_gateway.get_companies().with_id(company.id)

    def test_count_no_registered_company_if_none_was_created(self) -> None:
        assert len(self.database_gateway.get_companies()) == 0

    def test_count_one_registered_company_if_one_was_created(self) -> None:
        self.company_generator.create_company_record()
        assert len(self.database_gateway.get_companies()) == 1

    def test_that_get_all_companies_returns_all_companies(self) -> None:
        expected_company1 = self.company_generator.create_company_record(
            email="company1@provider.de"
        )
        expected_company2 = self.company_generator.create_company_record(
            email="company2@provider.de"
        )
        all_companies = list(self.database_gateway.get_companies())
        assert company_in_companies(expected_company1, all_companies)
        assert company_in_companies(expected_company2, all_companies)


class CreateCompanyTests(CompanyResultTests):
    def setUp(self) -> None:
        super().setUp()
        self.db = self.injector.get(SQLAlchemy)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_company_can_be_created_while_member_with_same_email_exists(
        self,
    ) -> None:
        expected_email_address = "test@test.test"
        self.member_generator.create_member(email=expected_email_address)
        credentials = (
            self.database_gateway.get_account_credentials()
            .with_email_address(expected_email_address)
            .first()
        )
        assert credentials
        self.create_company_from_credentials(credentials=credentials.id)
        self.db.session.flush()


class ThatAreWorkplaceOfMemberTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_by_default_random_members_are_not_assigned_to_a_company(self) -> None:
        self.company_generator.create_company()
        member = self.member_generator.create_member()
        assert not self.database_gateway.get_companies().that_are_workplace_of_member(
            member
        )

    def test_that_companies_are_retrieved_if_member_is_explict_worker_at_company(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.company_generator.create_company(workers=[member])
        assert self.database_gateway.get_companies().that_are_workplace_of_member(
            member
        )

    def test_that_workplace_is_returned_after_one_is_registered(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()
        self.database_gateway.get_companies().with_id(company).add_worker(member)
        assert (
            self.database_gateway.get_companies()
            .that_are_workplace_of_member(member)
            .with_id(company)
        )


class WithNameContainingTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_companies_can_be_filtered_by_name(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.database_gateway.get_companies().with_name_containing("abc123")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_subset_of_name(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.database_gateway.get_companies().with_name_containing("bc1")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_subset_of_name_regardless_of_case(self):
        expected_company_id = self.company_generator.create_company(name="abc123")
        returned_company = list(
            self.database_gateway.get_companies().with_name_containing("bC1")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id


class WithEmailContainingTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_companies_can_be_filtered_by_email(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_companies = list(
            self.database_gateway.get_companies().with_email_containing(
                "some.mail@cp.org"
            )
        )
        assert returned_companies
        assert returned_companies[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_email_case_insensitive(self):
        email = "some.mail@cp.org"
        expected_company_id = self.company_generator.create_company(email=email)
        altered_email = Utility.mangle_case(email)
        returned_companies = list(
            self.database_gateway.get_companies().with_email_containing(altered_email)
        )
        assert returned_companies[0].id == expected_company_id

    def test_that_companies_can_be_filtered_by_substring_of_email(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_company = list(
            self.database_gateway.get_companies().with_email_containing("ail@cp")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id

    def test_that_companies_can_be_filtered_regardless_of_case(self):
        expected_company_id = self.company_generator.create_company(
            email="some.mail@cp.org"
        )
        returned_company = list(
            self.database_gateway.get_companies().with_email_containing("aIL@cp")
        )
        assert returned_company
        assert returned_company[0].id == expected_company_id


class JoinedWithEmailTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_company_email_is_yielded(self) -> None:
        expected_email = "test@test.test"
        company = self.company_generator.create_company(email=expected_email)
        record = (
            self.database_gateway.get_companies()
            .with_id(company)
            .joined_with_email_address()
            .first()
        )
        assert record


class ThatIsCoordinatingCooperationTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_that_unrelated_company_is_not_included(self) -> None:
        company = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation()
        assert (
            not self.database_gateway.get_companies()
            .with_id(company)
            .that_is_coordinating_cooperation(cooperation.id)
        )

    def test_that_coordinator_is_included(self) -> None:
        company = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(coordinator=company)
        assert (
            self.database_gateway.get_companies()
            .with_id(company)
            .that_is_coordinating_cooperation(cooperation.id)
        )
