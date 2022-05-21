from typing import Callable, Optional, cast
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_accountant_profile_info import (
    GetAccountantProfileInfoUseCase,
)
from tests.data_generators import AccountantGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.get_profile_use_case = self.injector.get(GetAccountantProfileInfoUseCase)
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def test_that_user_can_see_correct_email_if_they_registered_with_test_mail_address(
        self,
    ) -> None:
        email_address = "test@test.test"
        user_id = self.accountant_generator.create_accountant(
            email_address=email_address
        )
        response = self.get_profile_use_case.get_accountant_profile_info(
            request=GetAccountantProfileInfoUseCase.Request(user_id=user_id)
        )
        self.assertRecord(response, lambda r: r.email_address == email_address)

    def test_that_user_can_see_correct_email_if_they_registered_with_another_test_mail_address(
        self,
    ) -> None:
        email_address = "test2@test.test"
        user_id = self.accountant_generator.create_accountant(
            email_address=email_address
        )
        response = self.get_profile_use_case.get_accountant_profile_info(
            request=GetAccountantProfileInfoUseCase.Request(user_id=user_id)
        )
        self.assertRecord(response, lambda r: r.email_address == email_address)

    def test_can_see_user_name_that_accountant_registered_with(self) -> None:
        expected_name = "test name"
        user_id = self.accountant_generator.create_accountant(name=expected_name)
        response = self.get_profile_use_case.get_accountant_profile_info(
            request=GetAccountantProfileInfoUseCase.Request(user_id=user_id)
        )
        self.assertRecord(response, lambda r: r.name == expected_name)

    def test_can_see_another_user_name_that_accountant_registered_with(self) -> None:
        expected_name = "test name2"
        user_id = self.accountant_generator.create_accountant(name=expected_name)
        response = self.get_profile_use_case.get_accountant_profile_info(
            request=GetAccountantProfileInfoUseCase.Request(user_id=user_id)
        )
        self.assertRecord(response, lambda r: r.name == expected_name)

    def test_get_no_record_for_random_uuid(self) -> None:
        response = self.get_profile_use_case.get_accountant_profile_info(
            request=GetAccountantProfileInfoUseCase.Request(user_id=uuid4())
        )
        self.assertIsNone(response.record)

    def assertRecord(
        self,
        response: GetAccountantProfileInfoUseCase.Response,
        condition: Optional[
            Callable[[GetAccountantProfileInfoUseCase.Record], bool]
        ] = None,
    ) -> None:
        self.assertIsInstance(response.record, GetAccountantProfileInfoUseCase.Record)
        if condition is not None:
            self.assertTrue(
                condition(cast(GetAccountantProfileInfoUseCase.Record, response.record))
            )
