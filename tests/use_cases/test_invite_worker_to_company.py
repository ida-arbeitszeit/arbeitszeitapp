from uuid import uuid4

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from tests.work_invitation_presenter import InviteWorkerPresenterImpl

from .base_test_case import BaseTestCase


class InviteWorkerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company_entity()
        self.member = self.member_generator.create_member_entity()
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_can_successfully_invite_worker_which_was_not_previously_invited(
        self,
    ) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_twices(self) -> None:
        request = InviteWorkerToCompanyUseCase.Request(
            company=self.company.id,
            worker=self.member.id,
        )
        self.invite_worker_to_company(request)
        response = self.invite_worker_to_company(request)
        assert not response.is_success

    def test_can_invite_different_workers(self) -> None:
        first_member = self.member_generator.create_member_entity()
        second_member = self.member_generator.create_member_entity()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=first_member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=second_member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_can_invite_same_worker_to_different_companies(self) -> None:
        first_company = self.company_generator.create_company_entity()
        second_company = self.company_generator.create_company_entity()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=first_company.id,
                worker=self.member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=second_company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=uuid4(),
            )
        )
        self.assertFalse(response.is_success)

    def test_cannot_invite_worker_to_company_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=uuid4(),
                worker=self.member.id,
            )
        )
        self.assertFalse(response.is_success)

    def test_response_uuid_is_not_none_on_successful_invite(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.assertIsNotNone(response.invite_id)


class NotificationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.company_generator.create_company_entity()
        self.member = self.member_generator.create_member_entity()
        self.invite_worker_presenter = self.injector.get(InviteWorkerPresenterImpl)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)

    def test_no_invite_gets_send_if_invite_was_not_successful(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=uuid4(),
            )
        )
        invites = self.invite_worker_presenter.invites
        self.assertEqual(len(invites), 0)

    def test_one_worker_gets_notified_on_successful_invite(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        invites = self.invite_worker_presenter.invites
        self.assertEqual(len(invites), 1)

    def test_correct_worker_gets_notified_on_successful_invite(self) -> None:
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        invites = self.invite_worker_presenter.invites
        self.assertEqual(invites[0].worker_email, self.member.email)

    def test_worker_gets_notified_about_correct_invite(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        invites = self.invite_worker_presenter.invites
        self.assertEqual(invites[0].id, response.invite_id)
