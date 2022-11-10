from typing import Callable, cast
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import (
    InviteWorkerToCompanyUseCase,
    ShowCompanyWorkInviteDetailsRequest,
    ShowCompanyWorkInviteDetailsResponse,
    ShowCompanyWorkInviteDetailsUseCase,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class TestNonExistingUserAndNonExistingInvite(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowCompanyWorkInviteDetailsUseCase)
        self.request = ShowCompanyWorkInviteDetailsRequest(
            invite=uuid4(),
            member=uuid4(),
        )
        self.response = self.use_case.show_company_work_invite_details(self.request)

    def test_response_is_marked_as_unsuccessful(self) -> None:
        self.assertFalse(self.response.is_success)


class TestExistingMemberWithNonMatchingInvite(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowCompanyWorkInviteDetailsUseCase)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_worker = self.injector.get(InviteWorkerToCompanyUseCase)
        self.invited_member = self.member_generator.create_member_entity()
        self.other_member = self.member_generator.create_member_entity()
        self.company = self.company_generator.create_company_entity()
        invite_response = self.invite_worker(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.invited_member.id,
            )
        )
        self.invite_id = invite_response.invite_id
        assert self.invite_id
        request = ShowCompanyWorkInviteDetailsRequest(
            invite=self.invite_id,
            member=self.other_member.id,
        )
        self.response = self.use_case.show_company_work_invite_details(request)

    def test_that_response_is_marked_as_unsuccessful(self) -> None:
        self.assertFalse(self.response.is_success)


class TestExistingMemberWithoutAnyInviteTest(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowCompanyWorkInviteDetailsUseCase)
        self.member_generator = self.injector.get(MemberGenerator)
        self.invited_member = self.member_generator.create_member_entity()
        request = ShowCompanyWorkInviteDetailsRequest(
            invite=uuid4(),
            member=self.invited_member.id,
        )
        self.response = self.use_case.show_company_work_invite_details(request)

    def test_that_response_is_marked_as_unsuccessful(self) -> None:
        self.assertFalse(self.response.is_success)


class TestExistingMemberWithMatchingInvite(TestCase):
    def setUp(self) -> None:
        self.expected_company_name = "test company name 123"
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ShowCompanyWorkInviteDetailsUseCase)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_worker = self.injector.get(InviteWorkerToCompanyUseCase)
        self.member = self.member_generator.create_member_entity()
        self.company = self.company_generator.create_company_entity(
            name=self.expected_company_name
        )
        invite_response = self.invite_worker(
            InviteWorkerToCompanyUseCase.Request(
                company=self.company.id,
                worker=self.member.id,
            )
        )
        self.invite_id = invite_response.invite_id
        assert self.invite_id
        request = ShowCompanyWorkInviteDetailsRequest(
            invite=self.invite_id,
            member=self.member.id,
        )
        self.response = self.use_case.show_company_work_invite_details(request)

    def test_response_is_marked_as_success(self) -> None:
        self.assertTrue(self.response.is_success)

    def test_expect_company_name_in_invite_details(self) -> None:
        self.assertDetails(lambda d: d.company_name == self.expected_company_name)

    def test_expect_invite_id_in_details(self) -> None:
        self.assertDetails(lambda d: d.invite_id == self.invite_id)

    def assertDetails(
        self, condition: Callable[[ShowCompanyWorkInviteDetailsResponse.Details], bool]
    ) -> None:
        details = self.response.details
        self.assertIsNotNone(details)
        self.assertTrue(
            condition(cast(ShowCompanyWorkInviteDetailsResponse.Details, details))
        )
