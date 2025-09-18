from datetime import timedelta
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.www.controllers.change_user_email_address_controller import (
    ChangeUserEmailAddressController,
)
from tests.datetime_service import datetime_utc
from tests.forms import ConfirmEmailAddressChangeFormImpl
from tests.www.base_test_case import BaseTestCase


class ExtractEmailAddressesControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ChangeUserEmailAddressController)

    @parameterized.expand(
        [
            (timedelta(minutes=15, seconds=1),),
            (timedelta(days=1),),
        ]
    )
    def test_that_no_result_is_returned_when_token_is_older_than_15_minutes(
        self,
        td: timedelta,
    ) -> None:
        TOKEN_CREATION = datetime_utc(2020, 1, 1)
        self.datetime_service.freeze_time(TOKEN_CREATION)
        token = self.token_service.generate_token(input="old_email:new_email")
        self.datetime_service.freeze_time(TOKEN_CREATION + td)
        result = self.controller.extract_email_addresses_from_token(token)
        assert result is None

    @parameterized.expand(
        [
            (timedelta(minutes=15, seconds=-1),),
            (timedelta(minutes=0),),
        ]
    )
    def test_that_a_result_is_returned_when_token_is_valid_and_less_than_15_minutes_old(
        self,
        td: timedelta,
    ) -> None:
        TOKEN_CREATION = datetime_utc(2020, 1, 1)
        self.datetime_service.freeze_time(TOKEN_CREATION)
        token = self.token_service.generate_token(input="old_email:new_email")
        self.datetime_service.freeze_time(TOKEN_CREATION + td)
        result = self.controller.extract_email_addresses_from_token(token)
        assert result is not None

    @parameterized.expand(
        [
            ("",),
            ("old_email",),
            (":new_email",),
            ("old_email:",),
            (":",),
            ("old_email-new_email",),
            ("old_email:new_email:extra",),
        ]
    )
    def test_that_no_result_is_returned_when_token_is_invalid(
        self, token_input: str
    ) -> None:
        token = self.token_service.generate_token(input=token_input)
        result = self.controller.extract_email_addresses_from_token(token)
        assert result is None

    def test_that_old_email_and_new_email_are_extracted_from_token(self) -> None:
        token = self.token_service.generate_token(input="old@mail.org:new@mail.org")
        result = self.controller.extract_email_addresses_from_token(token)
        assert result
        assert result == ("old@mail.org", "new@mail.org")


class CreateInteractorRequestTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ChangeUserEmailAddressController)

    def test_when_no_user_is_logged_in_return_none(self) -> None:
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=True)
        result = self.controller.create_interactor_request("new_email", form)
        assert result is None

    def test_when_form_is_not_accepted_return_none(self) -> None:
        self.session.login_company(uuid4())
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=False)
        result = self.controller.create_interactor_request("new_email", form)
        assert result is None

    def test_when_form_is_not_accepted_notify_user(self) -> None:
        self.session.login_company(uuid4())
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=False)
        assert not self.notifier.infos
        self.controller.create_interactor_request("new_email", form)
        assert self.notifier.infos

    def test_when_form_is_accepted_return_request(self) -> None:
        self.session.login_company(uuid4())
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=True)
        result = self.controller.create_interactor_request("new_email", form)
        assert result

    def test_when_form_is_accepted_return_request_with_new_email(self) -> None:
        self.session.login_company(uuid4())
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=True)
        result = self.controller.create_interactor_request("new_email", form)
        assert result
        assert result.new_email == "new_email"

    def test_when_form_is_accepted_return_request_with_current_user(self) -> None:
        company_id = uuid4()
        self.session.login_company(company_id)
        form = ConfirmEmailAddressChangeFormImpl(is_accepted=True)
        result = self.controller.create_interactor_request("new_email", form)
        assert result
        assert result.user == company_id
