from arbeitszeit import email_notifications
from arbeitszeit.use_cases import get_member_dashboard
from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase
from arbeitszeit.use_cases.get_member_dashboard import GetMemberDashboardUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.register_member import RegisterMemberUseCase

from .base_test_case import BaseTestCase

DEFAULT = dict(
    email="test@cp.org",
    name="test name",
    password="super safe",
)


class RegisterMemberTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RegisterMemberUseCase)
        self.login_use_case = self.injector.get(LogInMemberUseCase)
        self.get_member_dashboard_use_case = self.injector.get(
            GetMemberDashboardUseCase
        )
        self.confirm_company_use_case = self.injector.get(ConfirmCompanyUseCase)

    def test_that_a_token_is_sent_out_when_a_member_registers(self) -> None:
        self.use_case.register_member(RegisterMemberUseCase.Request(**DEFAULT))
        self.assertTrue(self.delivered_registration_mails())

    def test_that_token_was_delivered_to_registering_user(self) -> None:
        expected_email_address = "test@test.test"
        request_args = DEFAULT.copy()
        request_args.pop("email")
        self.use_case.register_member(
            RegisterMemberUseCase.Request(email=expected_email_address, **request_args)
        )
        self.assertEqual(
            self.latest_delivered_registration_mail().email_address,
            expected_email_address,
        )

    def test_confirmation_is_required_if_email_is_not_already_known(self) -> None:
        request_args = DEFAULT.copy()
        response = self.use_case.register_member(
            RegisterMemberUseCase.Request(**request_args)
        )
        assert response.is_confirmation_required

    def test_that_registering_member_is_possible(self) -> None:
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        self.assertFalse(response.is_rejected)

    def test_that_correct_member_attributes_are_registered(self) -> None:
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        assert response.user_id
        dashboard_request = get_member_dashboard.Request(member=response.user_id)
        dashboard_response = self.get_member_dashboard_use_case.get_member_dashboard(
            dashboard_request
        )
        assert dashboard_response.email == DEFAULT["email"]
        assert dashboard_response.name == DEFAULT["name"]

    def test_that_correct_error_is_raised_when_user_with_mail_exists(self) -> None:
        self.member_generator.create_member(email="test@cp.org")
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RegisterMemberUseCase.Response.RejectionReason.member_already_exists,
        )

    def test_no_confirmation_is_required_if_member_already_existed_pre_registration(
        self,
    ) -> None:
        self.member_generator.create_member(email="test@cp.org")
        request = RegisterMemberUseCase.Request(**DEFAULT)
        response = self.use_case.register_member(request)
        assert not response.is_confirmation_required

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

    def test_that_registration_is_denied_if_company_with_same_mail_already_exists_but_passwords_differ(
        self,
    ) -> None:
        expected_email = "test@test.test"
        self.company_generator.create_company(
            email=expected_email, password="test password"
        )
        register_response = self.use_case.register_member(
            RegisterMemberUseCase.Request(
                email=expected_email,
                name="test name",
                password="different password",
            )
        )
        assert register_response.is_rejected

    def test_that_registration_is_succesful_if_company_with_same_mail_already_exists_and_passwords_match(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "test password 123"
        self.company_generator.create_company(
            email=expected_email,
            password=expected_password,
        )
        register_response = self.use_case.register_member(
            RegisterMemberUseCase.Request(
                email=expected_email,
                name="test name",
                password=expected_password,
            )
        )
        assert not register_response.is_rejected

    def test_registering_a_member_with_same_email_as_company_does_not_require_company_to_reconfirm_email(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "test password 123"
        self.company_generator.create_company(
            email=expected_email,
            password=expected_password,
        )
        self.use_case.register_member(
            RegisterMemberUseCase.Request(
                email=expected_email,
                name="test name",
                password=expected_password,
            )
        )
        response = self.confirm_company_use_case.confirm_company(
            ConfirmCompanyUseCase.Request(email_address=expected_email)
        )
        assert not response.is_confirmed

    def test_that_no_confirmation_email_is_sent_out_if_registering_email_address_is_already_in_use_by_a_company(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "test password 123"
        self.company_generator.create_company(
            email=expected_email,
            password=expected_password,
        )
        pre_registration_confirmation_tokens = len(self.delivered_registration_mails())
        self.use_case.register_member(
            RegisterMemberUseCase.Request(
                email=expected_email,
                name="test name",
                password=expected_password,
            )
        )
        assert (
            len(self.delivered_registration_mails())
            == pre_registration_confirmation_tokens
        )

    def test_that_email_confirmation_is_not_required_if_email_is_already_confirmed_for_matching_company(
        self,
    ) -> None:
        expected_email = "test@test.test"
        expected_password = "test password 123"
        self.company_generator.create_company(
            email=expected_email,
            password=expected_password,
        )
        response = self.use_case.register_member(
            RegisterMemberUseCase.Request(
                email=expected_email,
                name="test name",
                password=expected_password,
            )
        )
        assert not response.is_confirmation_required

    def latest_delivered_registration_mail(
        self,
    ) -> email_notifications.MemberRegistration:
        mails = self.delivered_registration_mails()
        assert mails
        return mails[-1]

    def delivered_registration_mails(
        self,
    ) -> list[email_notifications.MemberRegistration]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.MemberRegistration)
        ]
