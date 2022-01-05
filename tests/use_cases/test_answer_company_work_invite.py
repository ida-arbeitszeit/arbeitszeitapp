from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.repositories import CompanyWorkerRepository, WorkerInviteRepository
from arbeitszeit.use_cases import (
    AnswerCompanyWorkInvite,
    AnswerCompanyWorkInviteRequest,
    InviteWorkerToCompany,
    InviteWorkerToCompanyRequest,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class AnwerCompanyWorkInviteTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.answer_company_work_invite = self.injector.get(AnswerCompanyWorkInvite)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompany)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_repository = self.injector.get(WorkerInviteRepository)  # type: ignore
        self.company_worker_repository = self.injector.get(CompanyWorkerRepository)  # type: ignore
        self.company = self.company_generator.create_company()
        self.member = self.member_generator.create_member()

    def test_trying_to_answer_non_existing_invite_is_unsuccessful(self) -> None:
        response = self.answer_company_work_invite(
            self._create_request(is_accepted=True, invite_id=uuid4())
        )
        self.assertFalse(response.is_success)

    def test_trying_to_answer_non_existing_invite_marks_response_as_rejected(
        self,
    ) -> None:
        response = self.answer_company_work_invite(
            self._create_request(is_accepted=True, invite_id=uuid4())
        )
        self.assertFalse(response.is_accepted)

    def test_rejecting_existing_invite_is_successful(self) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=False,
                invite_id=invite_id,
            )
        )
        self.assertTrue(response.is_success)

    def test_that_rejecting_an_invite_marks_response_as_rejected(self) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=False,
                invite_id=invite_id,
            )
        )
        self.assertFalse(response.is_accepted)

    def test_accepting_an_invite_adds_member_to_company_workers(self) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=True,
                invite_id=invite_id,
            )
        )
        repository = self.injector.get(CompanyWorkerRepository)  # type: ignore
        self.assertIn(self.member, repository.get_company_workers(self.company))
        self.assertTrue(response.is_success)

    def test_accepting_an_invite_marks_response_as_accepted(self) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=True,
                invite_id=invite_id,
            )
        )
        self.assertTrue(response.is_accepted)

    def test_rejecting_an_invite_does_not_add_member_to_company_workers(self) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=False,
                invite_id=invite_id,
            )
        )
        self.assertNotIn(
            self.member,
            self.company_worker_repository.get_company_workers(self.company),
        )
        self.assertTrue(response.is_success)

    def test_invite_gets_deleted_after_rejecting_an_invite(self) -> None:
        invite_id = self._invite_worker()
        self.answer_company_work_invite(
            self._create_request(
                is_accepted=False,
                invite_id=invite_id,
            )
        )
        self.assertIsNone(self.invite_repository.get_by_id(invite_id))

    def test_answer_invite_as_non_existing_member_returns_negative_reponse(
        self,
    ) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=True,
                invite_id=invite_id,
                user=uuid4(),
            )
        )
        self.assertFalse(response.is_success)

    def test_answer_invite_as_non_existing_member_marks_response_as_rejected(
        self,
    ) -> None:
        invite_id = self._invite_worker()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=True,
                invite_id=invite_id,
                user=uuid4(),
            )
        )
        self.assertFalse(response.is_accepted)

    def test_answer_invite_as_member_that_was_not_invited_returns_negative_reponse(
        self,
    ) -> None:
        invite_id = self._invite_worker()
        other_member = self.member_generator.create_member()
        response = self.answer_company_work_invite(
            self._create_request(
                is_accepted=True,
                invite_id=invite_id,
                user=other_member.id,
            )
        )
        self.assertFalse(response.is_success)

    def _invite_worker(self) -> UUID:
        invite_response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                self.company.id,
                self.member.id,
            )
        )
        invite_id = invite_response.invite_id
        assert invite_id
        return invite_id

    def _create_request(
        self, invite_id: UUID, is_accepted: bool, user: Optional[UUID] = None
    ) -> AnswerCompanyWorkInviteRequest:
        if user is None:
            user = self.member.id
        return AnswerCompanyWorkInviteRequest(
            invite_id=invite_id,
            is_accepted=is_accepted,
            user=user,
        )
