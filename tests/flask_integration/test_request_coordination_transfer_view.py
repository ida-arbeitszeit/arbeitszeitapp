from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class RequestCoordinationTransferTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_users_get_expected_status_codes_on_get_requests_when_cooperation_in_url_exists(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        self.assert_response_has_expected_code(
            url=f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_company_gets_404_on_get_request_when_cooperation_in_url_does_not_exist(
        self,
    ) -> None:
        self.assert_response_has_expected_code(
            url="company/cooperation_summary/1/request_coordination_transfer",
            method="get",
            expected_code=404,
            login=LogInUser.company,
        )

    def test_company_gets_code_403_on_post_request_when_current_user_is_not_coordinator(
        self,
    ) -> None:
        self.login_company().id
        cooperation = self.cooperation_generator.create_cooperation()
        candidate = self.company_generator.create_company()
        data = {"candidate": str(candidate), "cooperation": str(cooperation)}
        response = self.client.post(
            f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
            data=data,
        )
        assert response.status_code == 403

    def test_no_request_mail_is_sent_when_current_user_is_not_coordinator(
        self,
    ) -> None:
        self.login_company()
        cooperation = self.cooperation_generator.create_cooperation()
        candidate = self.company_generator.create_company()
        data = {"candidate": str(candidate), "cooperation": str(cooperation)}
        with self.email_service().record_messages() as outbox:
            response = self.client.post(
                f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
                data=data,
            )
            assert response.status_code == 403
            assert len(outbox) == 0

    def test_request_mail_is_sent_when_current_user_is_coordinator(
        self,
    ) -> None:
        current_user = self.login_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=current_user.id
        )
        candidate_mail = "candidate@mail.org"
        candidate = self.company_generator.create_company(email=candidate_mail)
        data = {"candidate": str(candidate), "cooperation": str(cooperation)}
        with self.email_service().record_messages() as outbox:
            response = self.client.post(
                f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
                data=data,
            )
            assert response.status_code == 200
            assert len(outbox) == 1
            assert outbox[0].recipients[0] == candidate_mail

    def test_second_request_with_identical_data_will_fail_with_code_409(
        self,
    ) -> None:
        current_user = self.login_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=current_user.id
        )
        candidate_mail = "candidate@mail.org"
        candidate = self.company_generator.create_company(email=candidate_mail)
        data = {"candidate": str(candidate), "cooperation": str(cooperation)}
        response = self.client.post(
            f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
            data=data,
        )
        assert response.status_code == 200

        response = self.client.post(
            f"company/cooperation_summary/{cooperation}/request_coordination_transfer",
            data=data,
        )
        assert response.status_code == 409
