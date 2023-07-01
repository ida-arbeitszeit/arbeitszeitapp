from uuid import uuid4

from arbeitszeit.use_cases import get_user_account_details

from .base_test_case import BaseTestCase


class GetUserAccountDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            get_user_account_details.GetUserAccountDetailsUseCase
        )

    def test_that_no_user_info_is_returned_if_requested_user_id_is_not_registered(
        self,
    ) -> None:
        request = get_user_account_details.Request(user_id=uuid4())
        response = self.use_case.get_user_account_details(request)
        assert response.user_info is None

    def test_that_returned_user_id_is_equal_to_member_id_requested(self) -> None:
        member = self.member_generator.create_member()
        request = get_user_account_details.Request(user_id=member)
        response = self.use_case.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == member

    def test_that_returned_user_id_is_equal_to_company_id_requested(self) -> None:
        company = self.company_generator.create_company()
        request = get_user_account_details.Request(user_id=company)
        response = self.use_case.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == company

    def test_that_returned_user_id_is_equal_to_accountant_id_requested(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        request = get_user_account_details.Request(user_id=accountant)
        response = self.use_case.get_user_account_details(request)
        assert response.user_info
        assert response.user_info.id == accountant

    def test_that_users_email_address_is_shown(self) -> None:
        for expected_email_address in [
            "testmail@test.test",
            "other@test.mail",
        ]:
            member = self.member_generator.create_member(email=expected_email_address)
            request = get_user_account_details.Request(user_id=member)
            response = self.use_case.get_user_account_details(request)
            assert response.user_info
            assert response.user_info.email_address == expected_email_address
