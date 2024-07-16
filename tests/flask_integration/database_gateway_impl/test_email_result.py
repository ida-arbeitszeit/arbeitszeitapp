from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from tests.data_generators import CompanyGenerator, MemberGenerator

from ..flask import FlaskTestCase
from .utility import Utility


class EmailAddressResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)


class CreateEmailAddressTests(EmailAddressResultTests):
    def test_cannot_create_same_email_address_twice(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=address, confirmed_on=datetime.min
            )

    def test_cannot_create_similar_email_address_case_insensitive(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        altered_address = Utility.mangle_case(address)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=altered_address, confirmed_on=datetime.min
            )


class ThatBelongToMemberTests(EmailAddressResultTests):
    def test_that_member_email_addresses_is_included(self) -> None:
        member = self.member_generator.create_member()
        assert self.database_gateway.get_email_addresses().that_belong_to_member(member)

    def test_that_companies_are_not_included(self) -> None:
        company = self.company_generator.create_company()
        assert not self.database_gateway.get_email_addresses().that_belong_to_member(
            company
        )


class ThatBelongToCompanyTests(EmailAddressResultTests):
    def test_that_members_are_not_included(self) -> None:
        member = self.member_generator.create_member()
        assert not self.database_gateway.get_email_addresses().that_belong_to_company(
            member
        )

    def test_that_companies_are_included(self) -> None:
        company = self.company_generator.create_company()
        assert self.database_gateway.get_email_addresses().that_belong_to_company(
            company
        )


class DeleteTests(EmailAddressResultTests):
    def test_can_delete_email_address(self) -> None:
        ADDRESS = "example@mail.org"
        assert not self.database_gateway.get_email_addresses()
        self.database_gateway.create_email_address(address=ADDRESS, confirmed_on=None)
        assert self.database_gateway.get_email_addresses()
        self.database_gateway.get_email_addresses().with_address(ADDRESS).delete()
        assert not self.database_gateway.get_email_addresses()
