from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from ..flask import FlaskTestCase


class EmailResultTests(FlaskTestCase):
    def test_cannot_create_same_email_address_twice(self) -> None:
        address = "test@test.test"
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        with pytest.raises(IntegrityError):
            self.database_gateway.create_email_address(
                address=address, confirmed_on=datetime.min
            )
