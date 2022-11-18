from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import RegisterMemberUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from tests.token import TokenDeliveryService

from .base_test_case import BaseTestCase
from .repositories import AccountRepository, MemberRepository

DEFAULT = dict(
    email="test@cp.org",
    name="test name",
    password="super safe",
)


class RegisterMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RegisterMemberUseCase)
        self.account_repository = self.injector.get(AccountRepository)
        self.member_repo = self.injector.get(MemberRepository)
        self.token_delivery = self.injector.get(TokenDeliveryService)
        self.login_use_case = self.injector.get(LogInMemberUseCase)

    def test_that_a_token_is_sent_out_when_a_member_registers(self) -> None:
        self.use_case.register_member(RegisterMemberUseCase.Request(**DEFAULT))
        self.assertTrue(self.token_delivery.presented_member_tokens)

    def test_that_token_was_delivered_to_registering_user(self) -> None:
        request_args = DEFAULT.copy()
        request_args.pop("email")
        self.use_case.register_member(
            RegisterMemberUseCase.Request(email="test@test.test", **request_args)
        )
        expected_user = list(self.member_repo.members.keys())[0]
        self.assertEqual(
            self.token_delivery.presented_member_tokens[0].user,
            expected_user,
        )

    def test_that_registering_member_is_possible(self) -> None:
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        self.assertFalse(response.is_rejected)

    def test_that_registering_a_member_does_create_a_member_account(self) -> None:
        self.use_case.register_member(RegisterMemberUseCase.Request(**DEFAULT))
        self.assertEqual(len(self.account_repository.accounts), 1)
        self.assertEqual(
            self.account_repository.accounts[0].account_type, AccountTypes.member
        )

    def test_that_correct_member_attributes_are_registered(self) -> None:
        request = RegisterMemberUseCase.Request(**DEFAULT)
        self.use_case.register_member(request)
        assert len(self.member_repo.members) == 1
        for member in self.member_repo.members.values():
            self.assertEqual(member.email, request.email)
            self.assertEqual(member.name, request.name)
            self.assertIsNotNone(member.registered_on)
            self.assertIsNone(member.confirmed_on)

    def test_that_correct_error_is_raised_when_user_with_mail_exists(self) -> None:
        self.member_generator.create_member_entity(email="test@cp.org")
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RegisterMemberUseCase.Response.RejectionReason.member_already_exists,
        )

    def test_that_uuid_returned_is_the_same_as_when_logging_in(self) -> None:
        register_response = self.use_case.register_member(
            RegisterMemberUseCase.Request(**DEFAULT)
        )
        login_response = self.login_use_case.log_in_member(
            LogInMemberUseCase.Request(
                email=DEFAULT["email"],
                password=DEFAULT["password"],
            )
        )
        assert login_response.user_id == register_response.user_id
