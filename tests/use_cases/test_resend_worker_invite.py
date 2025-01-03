from uuid import UUID, uuid4

from arbeitszeit import email_notifications
from arbeitszeit.use_cases import (
    answer_company_work_invite,
    invite_worker_to_company,
    resend_work_invite,
)
from tests.use_cases.base_test_case import BaseTestCase


class ResendInviteTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.company = self.company_generator.create_company()
        self.worker = self.member_generator.create_member()
        self.use_case = self.injector.get(resend_work_invite.ResendWorkInviteUseCase)

    def invite_worker(self, company_id: UUID, worker_id: UUID) -> UUID:
        request = invite_worker_to_company.InviteWorkerToCompanyUseCase.Request(
            company=company_id,
            worker=worker_id,
        )
        use_case = self.injector.get(
            invite_worker_to_company.InviteWorkerToCompanyUseCase
        )
        response = use_case.invite_worker(request)
        assert response.rejection_reason is None
        assert response.invite_id
        return response.invite_id

    def answer_invite(
        self, invite_id: UUID, worker_id: UUID, is_accepted: bool
    ) -> None:
        request = answer_company_work_invite.AnswerCompanyWorkInviteRequest(
            is_accepted=is_accepted,
            invite_id=invite_id,
            user=worker_id,
        )
        use_case = self.injector.get(answer_company_work_invite.AnswerCompanyWorkInvite)
        response = use_case(request)
        assert response.is_success
        assert response.is_accepted == is_accepted


class ResendWorkerInviteTests(ResendInviteTestCase):
    def test_resending_invite_fails_when_worker_has_not_been_invited(self) -> None:
        request = resend_work_invite.Request(
            company=uuid4(),
            worker=uuid4(),
        )
        response = self.use_case.resend_work_invite(request)
        assert (
            response.rejection_reason
            == resend_work_invite.Response.RejectionReason.INVITE_DOES_NOT_EXIST
        )

    def test_resending_invite_fails_when_worker_has_rejected_previous_invite(
        self,
    ) -> None:
        invite_id = self.invite_worker(company_id=self.company, worker_id=self.worker)
        self.answer_invite(
            invite_id=invite_id, worker_id=self.worker, is_accepted=False
        )
        request = resend_work_invite.Request(
            company=self.company,
            worker=self.worker,
        )
        response = self.use_case.resend_work_invite(request)
        assert (
            response.rejection_reason
            == resend_work_invite.Response.RejectionReason.INVITE_DOES_NOT_EXIST
        )

    def test_resending_invite_fails_when_worker_has_accepted_previous_invite(
        self,
    ) -> None:
        invite_id = self.invite_worker(company_id=self.company, worker_id=self.worker)
        self.answer_invite(invite_id=invite_id, worker_id=self.worker, is_accepted=True)
        request = resend_work_invite.Request(
            company=self.company,
            worker=self.worker,
        )
        response = self.use_case.resend_work_invite(request)
        assert (
            response.rejection_reason
            == resend_work_invite.Response.RejectionReason.INVITE_DOES_NOT_EXIST
        )

    def test_resending_invite_succeeds_when_worker_has_been_invited_previously_and_neither_accepted_nor_rejected(
        self,
    ) -> None:
        company_id = self.company_generator.create_company()
        worker_id = self.member_generator.create_member()
        self.invite_worker(company_id, worker_id)
        request = resend_work_invite.Request(
            company=company_id,
            worker=worker_id,
        )
        response = self.use_case.resend_work_invite(request)
        assert response.rejection_reason is None


class NotificationTests(ResendInviteTestCase):
    def test_no_invite_gets_send_if_resending_was_not_successful(self) -> None:
        response = self.use_case.resend_work_invite(
            resend_work_invite.Request(
                company=uuid4(),
                worker=uuid4(),
            )
        )
        assert response.rejection_reason
        assert not self.get_sent_notifications()

    def test_worker_gets_two_notifications_when_invite_is_resend(self) -> None:
        self.invite_worker(self.company, self.worker)
        self.use_case.resend_work_invite(
            resend_work_invite.Request(
                company=self.company,
                worker=self.worker,
            )
        )
        assert len(self.get_sent_notifications()) == 2

    def test_correct_worker_gets_notified(self) -> None:
        expected_email = "test@test.test"
        company = self.company_generator.create_company()
        worker = self.member_generator.create_member(email=expected_email)
        self.invite_worker(company, worker)
        self.use_case.resend_work_invite(
            resend_work_invite.Request(
                company=company,
                worker=worker,
            )
        )
        for invite in self.get_sent_notifications():
            invite.worker_email == expected_email

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
