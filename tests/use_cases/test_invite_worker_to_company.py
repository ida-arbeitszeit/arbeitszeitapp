from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import InviteWorkerToCompany, InviteWorkerToCompanyRequest
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class InviteWorkerTests(TestCase):
    def setUp(self) -> None:
        injector = get_dependency_injector()
        self.company_generator = injector.get(CompanyGenerator)
        self.company = self.company_generator.create_company()
        self.member_generator = injector.get(MemberGenerator)
        self.member = self.member_generator.create_member()
        self.invite_worker_to_company = injector.get(InviteWorkerToCompany)

    def test_can_successfully_invite_worker_which_was_not_previously_invited(
        self,
    ) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_twices(self) -> None:
        request = InviteWorkerToCompanyRequest(
            company=self.company.id,
            worker=self.member.id,
        )
        self.invite_worker_to_company(request)
        response = self.invite_worker_to_company(request)
        assert not response.is_success

    def test_can_invite_different_workers(self) -> None:
        first_member = self.member_generator.create_member()
        second_member = self.member_generator.create_member()
        self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=self.company.id,
                worker=first_member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=self.company.id,
                worker=second_member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_can_invite_same_worker_to_different_companies(self) -> None:
        first_company = self.company_generator.create_company()
        second_company = self.company_generator.create_company()
        self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=first_company.id,
                worker=self.member.id,
            )
        )
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=second_company.id,
                worker=self.member.id,
            )
        )
        self.assertTrue(response.is_success)

    def test_cannot_invite_worker_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=self.company.id,
                worker=uuid4(),
            )
        )
        self.assertFalse(response.is_success)

    def test_cannot_invite_worker_to_company_that_does_not_exist(self) -> None:
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=uuid4(),
                worker=self.member.id,
            )
        )
        self.assertFalse(response.is_success)
