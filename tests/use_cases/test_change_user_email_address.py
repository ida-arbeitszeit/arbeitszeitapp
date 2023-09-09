from parameterized import parameterized

from arbeitszeit.use_cases import log_in_member
from arbeitszeit.use_cases.change_user_email_address import (
    ChangeUserEmailAddressUseCase,
    Request,
)

from .base_test_case import BaseTestCase


class ChangeUserEmailAddressTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ChangeUserEmailAddressUseCase)
        self.log_in_member_use_case = self.injector.get(
            log_in_member.LogInMemberUseCase
        )

    def test_that_request_for_email_with_no_existing_user_is_rejected(self) -> None:
        request = Request(old_email="test@test.test", new_email="new@test.test")
        response = self.use_case.change_user_email_address(request)
        assert response.is_rejected

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_request_for_email_with_existing_member_is_accepted(
        self, old_email: str
    ) -> None:
        self.member_generator.create_member(email=old_email)
        request = Request(old_email=old_email, new_email="new@test.test")
        response = self.use_case.change_user_email_address(request)
        assert not response.is_rejected

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_request_for_email_with_existing_company_is_accepted(
        self, old_email: str
    ) -> None:
        self.company_generator.create_company(email=old_email)
        request = Request(old_email=old_email, new_email="new@test.test")
        response = self.use_case.change_user_email_address(request)
        assert not response.is_rejected

    @parameterized.expand(
        [
            ("test@test.test",),
            ("other@test.test",),
        ]
    )
    def test_that_request_for_email_with_existing_accountant_is_accepted(
        self, old_email: str
    ) -> None:
        self.accountant_generator.create_accountant(email_address=old_email)
        request = Request(old_email=old_email, new_email="new@test.test")
        response = self.use_case.change_user_email_address(request)
        assert not response.is_rejected

    @parameterized.expand(
        [
            ("@",),
            (" @ ",),
            ("a@ ",),
        ]
    )
    def test_that_changing_the_email_address_to_something_that_is_definitly_not_an_email_address_is_rejected(
        self, new_email: str
    ) -> None:
        old_email = "test@test.test"
        self.accountant_generator.create_accountant(email_address=old_email)
        request = Request(old_email=old_email, new_email=new_email)
        response = self.use_case.change_user_email_address(request)
        assert response.is_rejected

    def test_that_request_is_rejected_if_new_email_is_already_in_use_by_other_member(
        self,
    ) -> None:
        old_email = "test@test.test"
        new_email = "new@test.test"
        self.member_generator.create_member(email=old_email)
        self.member_generator.create_member(email=new_email)
        request = Request(old_email=old_email, new_email=new_email)
        response = self.use_case.change_user_email_address(request)
        assert response.is_rejected

    def test_that_request_is_rejected_if_new_email_is_already_in_use_by_other_company(
        self,
    ) -> None:
        old_email = "test@test.test"
        new_email = "new@test.test"
        self.member_generator.create_member(email=old_email)
        self.company_generator.create_company(email=new_email)
        request = Request(old_email=old_email, new_email=new_email)
        response = self.use_case.change_user_email_address(request)
        assert response.is_rejected

    def test_that_request_is_rejected_if_new_email_is_already_in_use_by_other_accountant(
        self,
    ) -> None:
        old_email = "test@test.test"
        new_email = "new@test.test"
        self.member_generator.create_member(email=old_email)
        self.accountant_generator.create_accountant(email_address=new_email)
        request = Request(old_email=old_email, new_email=new_email)
        response = self.use_case.change_user_email_address(request)
        assert response.is_rejected

    def test_that_member_can_log_in_with_new_email_after_address_change(
        self,
    ) -> None:
        old_email = "test@test.test"
        new_email = "new@test.test"
        password = "test1234"
        self.member_generator.create_member(email=old_email, password=password)
        request = Request(old_email=old_email, new_email=new_email)
        self.use_case.change_user_email_address(request)
        assert self.can_log_in_member(email_address=new_email, password=password)

    def can_log_in_member(self, email_address: str, password: str) -> bool:
        response = self.log_in_member_use_case.log_in_member(
            request=log_in_member.LogInMemberUseCase.Request(
                email=email_address, password=password
            )
        )
        return response.is_logged_in
