from parameterized import parameterized

from arbeitszeit_web.www.controllers.request_email_address_change_controller import (
    RequestEmailAddressChangeController,
)
from tests.forms import RequestEmailAddressChangeFormImpl as Form

from ..base_test_case import BaseTestCase


class RequestEmailAddressChangeControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestEmailAddressChangeController)

    @parameterized.expand(
        [
            ("old@test.test", "new@test.test"),
            ("member@test.test", "new@test.test"),
            ("member@test.test", "new2@test.test"),
        ]
    )
    def test_that_for_authenticated_member_use_the_current_email_address_and_supplied_new_email_address_in_request(
        self, current_address: str, new_address: str
    ) -> None:
        member = self.member_generator.create_member(email=current_address)
        self.session.login_member(member=member)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address

    def test_that_for_authenticated_member_use_the_current_email_address_and_supplied_new_email_address_in_request_even_as_another_member_registered_before_them(
        self,
    ) -> None:
        current_address = "member@test.test"
        new_address = "new@test.test"
        self.member_generator.create_member(email="other@test.test")
        member = self.member_generator.create_member(email=current_address)
        self.session.login_member(member=member)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address

    @parameterized.expand(
        [
            ("old@test.test", "new@test.test"),
            ("company@test.test", "new@test.test"),
            ("company@test.test", "new2@test.test"),
        ]
    )
    def test_that_for_authenticated_company_use_the_current_email_address_and_supplied_new_email_address_in_request(
        self, current_address: str, new_address: str
    ) -> None:
        company = self.company_generator.create_company(email=current_address)
        self.session.login_company(company=company)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address

    def test_that_for_authenticated_company_use_the_current_email_address_and_supplied_new_email_address_in_request_even_as_another_company_registered_before_them(
        self,
    ) -> None:
        current_address = "company@test.test"
        new_address = "new@test.test"
        self.company_generator.create_company(email="other@test.test")
        company = self.company_generator.create_company(email=current_address)
        self.session.login_company(company=company)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address

    @parameterized.expand(
        [
            ("old@test.test", "new@test.test"),
            ("accountant@test.test", "new@test.test"),
            ("accountant@test.test", "new2@test.test"),
        ]
    )
    def test_that_for_authenticated_accountant_use_the_current_email_address_and_supplied_new_email_address_in_request(
        self, current_address: str, new_address: str
    ) -> None:
        accountant = self.accountant_generator.create_accountant(
            email_address=current_address
        )
        self.session.login_accountant(accountant=accountant)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address

    def test_that_for_authenticated_accountant_use_the_current_email_address_and_supplied_new_email_address_in_request_even_as_another_accountant_registered_before_them(
        self,
    ) -> None:
        current_address = "accountant@test.test"
        new_address = "new@test.test"
        self.accountant_generator.create_accountant(email_address="other@test.test")
        accountant = self.accountant_generator.create_accountant(
            email_address=current_address
        )
        self.session.login_accountant(accountant=accountant)
        form = Form.from_values(new_email_address=new_address)
        use_case_request = self.controller.process_email_address_change_request(form)
        assert use_case_request.current_email_address == current_address
        assert use_case_request.new_email_address == new_address
