from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.exc import IntegrityError

from tests.datetime_service import datetime_min_utc, datetime_utc
from tests.db.base_test_case import DatabaseTestCase

from .utility import Utility


class CreateEmailAddressTests(DatabaseTestCase):
    def test_created_email_address_contains_utc_confirmation_date(self) -> None:
        confirmation_date = datetime_utc(2023, 1, 2, 3, 4, 5)
        self.database_gateway.create_email_address(
            address="test@test.test",
            confirmed_on=confirmation_date,
        )
        email_address = self.database_gateway.get_email_addresses().first()
        assert email_address is not None
        assert email_address.confirmed_on == confirmation_date
        assert email_address.confirmed_on.tzinfo == UTC

    def test_returned_confirmation_date_gets_time_zone_changed_to_utc(self) -> None:
        original_date = datetime(2023, 1, 2, 3, 4, 5).astimezone(ZoneInfo("Asia/Tokyo"))
        self.database_gateway.create_email_address(
            address="test@test.test",
            confirmed_on=original_date,
        )
        email_address = self.database_gateway.get_email_addresses().first()
        assert email_address is not None
        assert email_address.confirmed_on == original_date
        assert email_address.confirmed_on.tzinfo != original_date.tzinfo
        assert email_address.confirmed_on.tzinfo == UTC

    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    def test_cannot_create_same_email_address_twice(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=address, confirmed_on=datetime_min_utc()
            )

    @pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
    def test_cannot_create_similar_email_address_case_insensitive(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        altered_address = Utility.mangle_case(address)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=altered_address, confirmed_on=datetime_min_utc()
            )


class ThatBelongToMemberTests(DatabaseTestCase):
    def test_that_member_email_addresses_is_included(self) -> None:
        member = self.member_generator.create_member()
        assert self.database_gateway.get_email_addresses().that_belong_to_member(member)

    def test_that_companies_are_not_included(self) -> None:
        company = self.company_generator.create_company()
        assert not self.database_gateway.get_email_addresses().that_belong_to_member(
            company
        )


class ThatBelongToCompanyTests(DatabaseTestCase):
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


class DeleteTests(DatabaseTestCase):
    def test_can_delete_email_address(self) -> None:
        ADDRESS = "example@mail.org"
        assert not self.database_gateway.get_email_addresses()
        self.database_gateway.create_email_address(address=ADDRESS, confirmed_on=None)
        assert self.database_gateway.get_email_addresses()
        self.database_gateway.get_email_addresses().with_address(ADDRESS).delete()
        assert not self.database_gateway.get_email_addresses()
