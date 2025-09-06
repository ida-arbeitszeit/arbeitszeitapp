from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import pytest
from parameterized import parameterized
from sqlalchemy.exc import IntegrityError

from arbeitszeit import records

from ..flask import FlaskTestCase
from .utility import Utility


class MemberResultTests(FlaskTestCase):
    def create_member(self, email_address: Optional[str] = None) -> records.Member:
        if email_address is None:
            email_address = self.email_generator.get_random_email()
        self.database_gateway.create_email_address(
            address=email_address, confirmed_on=None
        )
        credentials = self.database_gateway.create_account_credentials(
            password_hash="", email_address=email_address
        )
        return self.create_member_from_credentials(credentials=credentials.id)

    def create_member_from_credentials(self, *, credentials: UUID) -> records.Member:
        account = self.database_gateway.create_account()
        return self.database_gateway.create_member(
            name="karl",
            account=account,
            registered_on=self.datetime_service.now(),
            account_credentials=credentials,
        )


class RepositoryTests(MemberResultTests):
    def test_that_member_can_be_retrieved_by_id(self) -> None:
        expected_member = self.create_member()
        retrieved_member = (
            self.database_gateway.get_members().with_id(expected_member.id).first()
        )
        assert retrieved_member
        assert retrieved_member == expected_member

    def test_that_member_can_be_retrieved_by_email(self) -> None:
        expected_mail = "test_mail@testmail.com"
        expected_member = self.create_member(email_address=expected_mail)
        result = (
            self.database_gateway.get_members()
            .with_email_address(expected_mail)
            .first()
        )
        assert result == expected_member

    def test_that_member_can_be_retrieved_by_email_case_insensitive(self) -> None:
        expected_mail = "test_mail@testmail.com"
        altered_mail = Utility.mangle_case(expected_mail)
        expected_member = self.create_member(email_address=expected_mail)
        result = (
            self.database_gateway.get_members().with_email_address(altered_mail).first()
        )
        assert result == expected_member

    def test_that_random_email_returns_no_member(self) -> None:
        random_email = "xyz123@testmail.com"
        self.create_member(email_address="test_mail@testmail.com")
        assert not self.database_gateway.get_members().with_email_address(random_email)

    def test_cannot_find_member_by_email_before_it_was_added(self) -> None:
        members = self.database_gateway.get_members()
        expected_email_address = "member@cp.org"
        assert not members.with_email_address(expected_email_address)
        self.create_member(email_address=expected_email_address)
        assert members.with_email_address(expected_email_address)

    def test_does_not_identify_random_id_with_member(self) -> None:
        member_id = uuid4()
        assert not self.database_gateway.get_members().with_id(member_id)

    def test_does_not_identify_company_as_member(self) -> None:
        company = self.company_generator.create_company_record()
        assert not self.database_gateway.get_members().with_id(company.id)

    def test_does_identify_member_id_as_member(self) -> None:
        member = self.create_member()
        assert self.database_gateway.get_members().with_id(member.id)

    def test_member_count_is_0_when_none_were_created(self) -> None:
        assert len(self.database_gateway.get_members()) == 0

    def test_count_one_registered_member_when_one_was_created(self) -> None:
        self.create_member()
        assert len(self.database_gateway.get_members()) == 1

    def test_with_id_returns_no_members_when_member_does_not_exist(self) -> None:
        assert not self.database_gateway.get_members().with_id(uuid4())


class GetAllMembersTests(MemberResultTests):
    def test_with_empty_db_the_first_member_is_none(self) -> None:
        assert self.database_gateway.get_members().first() is None

    def test_with_one_member_id_db_the_first_element_is_that_member(self) -> None:
        expected_member = self.create_member()
        member = self.database_gateway.get_members().first()
        assert member
        assert member.id == expected_member.id

    def test_that_all_members_can_be_retrieved(self) -> None:
        expected_member1 = self.create_member()
        expected_member2 = self.create_member()
        all_members = list(self.database_gateway.get_members())
        assert expected_member1 in all_members
        assert expected_member2 in all_members

    @parameterized.expand(
        [
            (0,),
            (1,),
            (10,),
        ]
    )
    def test_that_number_of_returned_members_is_equal_to_number_of_created_members(
        self, member_count: int
    ) -> None:
        for i in range(member_count):
            self.create_member()
        member_count = len(self.database_gateway.get_members())
        assert member_count == member_count

    def test_can_filter_members_by_their_workplace(self) -> None:
        member = self.create_member()
        self.create_member()
        company = self.company_generator.create_company_record(workers=[member.id])
        assert len(self.database_gateway.get_members()) == 2
        assert (
            len(self.database_gateway.get_members().working_at_company(company.id)) == 1
        )


class ConfirmMemberTests(MemberResultTests):
    def setUp(self) -> None:
        super().setUp()
        self.timestamp = datetime(2000, 1, 1)

    def test_that_confirmed_on_gets_updated_for_affected_user(self) -> None:
        expected_timestamp = datetime(2000, 1, 2)
        email_address = "test@test.test"
        member = self.create_member(email_address=email_address)
        self.database_gateway.get_email_addresses().with_address(
            email_address
        ).update().set_confirmation_timestamp(expected_timestamp).perform()
        record = (
            self.database_gateway.get_members()
            .with_id(member.id)
            .joined_with_email_address()
            .first()
        )
        assert record
        _, email = record
        assert email.confirmed_on == expected_timestamp


class CreateMemberTests(MemberResultTests):
    def test_can_create_member_with_same_email_as_company(self) -> None:
        email = "test@test.test"
        self.company_generator.create_company(email=email)
        account_credentials = (
            self.database_gateway.get_account_credentials()
            .with_email_address(email)
            .first()
        )
        assert account_credentials
        self.create_member_from_credentials(credentials=account_credentials.id)

    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    def test_cannot_create_member_with_same_email_twice(self) -> None:
        email = "test@test.test"
        self.create_member(email_address=email)
        with self.assertRaises(IntegrityError):
            self.create_member(email_address=email)
