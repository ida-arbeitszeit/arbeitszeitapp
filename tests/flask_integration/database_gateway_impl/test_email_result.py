from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from .utility import Utility

from ..flask import FlaskTestCase


class EmailResultTests(FlaskTestCase):
    def test_cannot_create_same_email_address_twice(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=address, confirmed_on=datetime.min
            )

    def test_cannot_create_same_email_address_twice_case_insensitive(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        altered_address = Utility.mangle_case(address) 
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=altered_address, confirmed_on=datetime.min
            )
