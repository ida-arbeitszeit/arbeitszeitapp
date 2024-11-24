from uuid import uuid4

from parameterized import parameterized

from arbeitszeit import email_notifications
from arbeitszeit.use_cases import remove_worker_from_company
from tests.use_cases.base_test_case import BaseTestCase


class RemoveWorkerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            remove_worker_from_company.RemoveWorkerFromCompanyUseCase
        )

    def test_reject_removal_if_company_not_found(self) -> None:
        request = remove_worker_from_company.Request(worker=uuid4(), company=uuid4())
        response = self.use_case.remove_worker_from_company(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == remove_worker_from_company.Response.RejectionReason.company_not_found
        )

    def test_reject_removal_if_worker_not_found(self) -> None:
        company = self.company_generator.create_company()
        request = remove_worker_from_company.Request(worker=uuid4(), company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == remove_worker_from_company.Response.RejectionReason.worker_not_found
        )

    def test_reject_removal_if_worker_not_at_company(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company()
        request = remove_worker_from_company.Request(worker=worker, company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == remove_worker_from_company.Response.RejectionReason.not_workplace_of_worker
        )

    def test_reject_removal_if_different_worker_works_at_company(self) -> None:
        worker = self.member_generator.create_member()
        other_worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[other_worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == remove_worker_from_company.Response.RejectionReason.not_workplace_of_worker
        )

    def test_successful_worker_removal(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert not response.is_rejected

    def test_cannot_remove_worker_twice(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert not response.is_rejected
        response = self.use_case.remove_worker_from_company(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == remove_worker_from_company.Response.RejectionReason.not_workplace_of_worker
        )

    def test_can_remove_other_workers_after_removal(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        other_worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker, other_worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        response = self.use_case.remove_worker_from_company(request)
        assert not response.is_rejected
        request = remove_worker_from_company.Request(
            worker=other_worker, company=company
        )
        response = self.use_case.remove_worker_from_company(request)
        assert not response.is_rejected

    def test_no_notification_if_removal_fails(self) -> None:
        request = remove_worker_from_company.Request(worker=uuid4(), company=uuid4())
        self.use_case.remove_worker_from_company(request)
        notifications = self.get_sent_notifications()
        assert not notifications

    def test_send_notification_on_successful_removal(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        self.use_case.remove_worker_from_company(request)
        notifications = self.get_sent_notifications()
        assert len(notifications) == 1

    @parameterized.expand(
        [
            ("worker1@cp.org",),
            ("worker2@cp.org",),
        ]
    )
    def test_notification_sent_to_worker_email(self, email: str) -> None:
        worker = self.member_generator.create_member(email=email)
        company = self.company_generator.create_company(workers=[worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        self.use_case.remove_worker_from_company(request)
        notifications = self.get_sent_notifications()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.worker_email == email

    @parameterized.expand(
        [
            ("worker1@cp.org",),
            ("worker2@cp.org",),
        ]
    )
    def test_no_notification_to_other_worker_email(
        self,
        other_worker_email: str,
    ) -> None:
        worker = self.member_generator.create_member()
        other_worker = self.member_generator.create_member(email=other_worker_email)
        company = self.company_generator.create_company(workers=[worker, other_worker])
        request = remove_worker_from_company.Request(worker=worker, company=company)
        self.use_case.remove_worker_from_company(request)
        notifications = self.get_sent_notifications()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.worker_email != other_worker_email

    @parameterized.expand(
        [
            ("company1",),
            ("company 2",),
        ]
    )
    def test_notification_contains_company_name(self, company_name: str) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(
            name=company_name, workers=[worker]
        )
        request = remove_worker_from_company.Request(worker=worker, company=company)
        self.use_case.remove_worker_from_company(request)
        notifications = self.get_sent_notifications()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.company_name == company_name

    def get_sent_notifications(
        self,
    ) -> list[email_notifications.WorkerRemovalNotification]:
        return [
            m
            for m in self.email_sender.get_messages_sent()
            if isinstance(m, email_notifications.WorkerRemovalNotification)
        ]
