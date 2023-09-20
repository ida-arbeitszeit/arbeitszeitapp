from uuid import uuid4

from arbeitszeit import email_notifications
from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase

from .base_test_case import BaseTestCase


class InviteWorkerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.member = self.member_generator.create_member()
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_can_successfully_invite_worker_which_was_not_previously_invited(
        self,
    ) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_twices(self) -> None:
        request = InviteWorkerToCompanyUseCase.Request(
            company=self.company,
            worker=self.member,
        )
        self.invite_worker_to_company(request)
        response = self.invite_worker_to_company(request)
        assert not response.is_success

    def test_can_invite_different_workers(self) -> None:
        first_member = self.member_generator.create_member()
        second_member = self.member_generator.create_member()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=first_member,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=second_member,
            )
        )
        self.assertTrue(response.is_success)

    def test_can_invite_same_worker_to_different_companies(self) -> None:
        first_company = self.company_generator.create_company_record()
        second_company = self.company_generator.create_company_record()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=first_company.id,
                worker=self.member,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=second_company.id,
                worker=self.member,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=uuid4(),
            )
        )
        self.assertFalse(response.is_success)

    def test_cannot_invite_worker_to_company_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=uuid4(),
                worker=self.member,
            )
        )
        self.assertFalse(response.is_success)

    def test_response_uuid_is_not_none_on_successful_invite(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        self.assertIsNotNone(response.invite_id)


class NotificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.member = self.member_generator.create_member()
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_no_invite_gets_send_if_invite_was_not_successful(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=uuid4(),
            )
        )
        invites = self.get_sent_notifications()
        self.assertEqual(len(invites), 0)

    def test_one_worker_gets_notified_on_successful_invite(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        invites = self.get_sent_notifications()
        self.assertEqual(len(invites), 1)

    def test_correct_worker_gets_notified_on_successful_invite(self) -> None:
        expected_email = "test@test.test"
        company = self.company_generator.create_company()
        member = self.member_generator.create_member(email=expected_email)
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=company,
                worker=member,
            )
        )
        self.assertEqual(
            self.get_latest_invite_notification().worker_email, expected_email
        )

    def test_worker_gets_notified_about_correct_invite(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company,
                worker=self.member,
            )
        )
        self.assertEqual(
            self.get_latest_invite_notification().invite, response.invite_id
        )

    def get_latest_invite_notification(self) -> email_notifications.WorkerInvitation:
        notifications = self.get_sent_notifications()
        assert notifications
        return notifications[-1]

    def get_sent_notifications(self) -> list[email_notifications.WorkerInvitation]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.WorkerInvitation)
        ]
