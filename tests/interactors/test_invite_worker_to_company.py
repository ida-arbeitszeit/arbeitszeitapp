from uuid import uuid4

from arbeitszeit import email_notifications
from arbeitszeit.interactors.invite_worker_to_company import (
    InviteWorkerToCompanyInteractor,
)

from .base_test_case import BaseTestCase


class InviteWorkerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.member = self.member_generator.create_member()
        self.interactor = self.injector.get(InviteWorkerToCompanyInteractor)

    def test_same_company_cannot_invite_same_worker_twice(self) -> None:
        request = self.create_interactor_request()
        self.interactor.invite_worker(request)
        response = self.interactor.invite_worker(request)
        assert (
            response.rejection_reason
            == InviteWorkerToCompanyInteractor.Response.RejectionReason.INVITATION_ALREADY_ISSUED
        )

    def test_can_invite_different_workers(self) -> None:
        first_worker = self.member_generator.create_member()
        second_worker = self.member_generator.create_member()
        self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=first_worker,
            )
        )
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=second_worker,
            )
        )
        assert not response.rejection_reason
        assert response.invite_id

    def test_can_invite_same_worker_to_different_companies(self) -> None:
        first_company = self.company_generator.create_company()
        second_company = self.company_generator.create_company()
        self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=first_company,
                worker=self.member,
            )
        )
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=second_company,
                worker=self.member,
            )
        )
        assert not response.rejection_reason
        assert response.invite_id

    def test_cannot_invite_worker_that_does_not_exist(self) -> None:
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=uuid4(),
            )
        )
        assert (
            response.rejection_reason
            == InviteWorkerToCompanyInteractor.Response.RejectionReason.WORKER_NOT_FOUND
        )

    def test_cannot_invite_worker_to_company_that_does_not_exist(self) -> None:
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=uuid4(),
                worker=self.member,
            )
        )
        assert (
            response.rejection_reason
            == InviteWorkerToCompanyInteractor.Response.RejectionReason.COMPANY_NOT_FOUND
        )

    def test_cannot_invite_worker_that_already_works_for_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=company,
                worker=worker,
            )
        )
        assert (
            response.rejection_reason
            == InviteWorkerToCompanyInteractor.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY
        )

    def test_invite_id_in_response_is_not_none_on_successful_invite(self) -> None:
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=self.member,
            )
        )
        assert response.invite_id

    def create_interactor_request(self) -> InviteWorkerToCompanyInteractor.Request:
        return InviteWorkerToCompanyInteractor.Request(
            company=self.company,
            worker=self.member,
        )


class NotificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company()
        self.member = self.member_generator.create_member()
        self.interactor = self.injector.get(InviteWorkerToCompanyInteractor)

    def test_no_invite_gets_send_if_invite_was_not_successful(self) -> None:
        self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=uuid4(),
            )
        )
        invites = self.get_sent_notifications()
        assert not invites

    def test_one_worker_gets_notified_on_successful_invite(self) -> None:
        self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=self.member,
            )
        )
        invites = self.get_sent_notifications()
        assert len(invites) == 1

    def test_correct_worker_gets_notified_on_successful_invite(self) -> None:
        expected_email = "test@test.test"
        company = self.company_generator.create_company()
        member = self.member_generator.create_member(email=expected_email)
        self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=company,
                worker=member,
            )
        )
        assert self.get_latest_invite_notification().worker_email == expected_email

    def test_worker_gets_notified_about_correct_invite(self) -> None:
        response = self.interactor.invite_worker(
            InviteWorkerToCompanyInteractor.Request(
                company=self.company,
                worker=self.member,
            )
        )
        assert self.get_latest_invite_notification().invite == response.invite_id

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
