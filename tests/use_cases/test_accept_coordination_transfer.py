from uuid import UUID, uuid4

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit.use_cases.get_coop_summary import GetCoopSummary, GetCoopSummaryRequest
from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
)
from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase,
)
from tests.use_cases.base_test_case import BaseTestCase


class TestAcceptCoordinationTransferUseCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.use_case = self.injector.get(AcceptCoordinationTransferUseCase)
        self.list_coordinations_use_case = self.injector.get(
            ListCoordinationsOfCooperationUseCase
        )
        self.get_coop_summary_use_case = self.injector.get(GetCoopSummary)
        self.request_transfer_use_case = self.injector.get(
            RequestCoordinationTransferUseCase
        )

    def test_use_case_fails_if_coordination_transfer_request_does_not_exist(
        self,
    ) -> None:
        response = self.use_case.accept_coordination_transfer(
            AcceptCoordinationTransferUseCase.Request(
                transfer_request_id=uuid4(),
                accepting_company=self.company_generator.create_company(),
            )
        )
        assert response.is_rejected
        self.assertTrue(
            response.rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_not_found
        )

    def test_use_case_fails_if_coordination_transfer_request_has_already_been_accepted(
        self,
    ) -> None:
        request = self.create_use_case_request()
        self.use_case.accept_coordination_transfer(request)
        response = self.use_case.accept_coordination_transfer(request)
        assert response.is_rejected
        self.assertTrue(
            response.rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_closed
        )

    def test_use_case_fails_if_accepting_company_is_not_candidate(
        self,
    ) -> None:
        accepting_company = self.company_generator.create_company()
        candidate = self.company_generator.create_company()
        requester_and_coordinator = self.company_generator.create_company()
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester_and_coordinator,
            cooperation=self.cooperation_generator.create_cooperation(
                coordinator=requester_and_coordinator
            ),
            candidate=candidate,
        )
        response = self.use_case.accept_coordination_transfer(
            request=AcceptCoordinationTransferUseCase.Request(
                transfer_request_id=transfer_request,
                accepting_company=accepting_company,
            )
        )
        assert response.is_rejected
        self.assertTrue(
            response.rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.accepting_company_is_not_candidate
        )

    def test_use_case_succeeds_if_coordination_transfer_request_exists_and_is_open(
        self,
    ) -> None:
        request = self.create_use_case_request()
        response = self.use_case.accept_coordination_transfer(request)
        self.assertFalse(response.is_rejected)

    def test_after_accepting_the_candidate_is_one_of_the_coordinators_of_cooperation(
        self,
    ) -> None:
        present_coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=present_coordinator
        )
        candidate_and_expected_coordinator = self.company_generator.create_company()

        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=present_coordinator,
            cooperation=cooperation,
            candidate=candidate_and_expected_coordinator,
        )

        self.use_case.accept_coordination_transfer(
            request=AcceptCoordinationTransferUseCase.Request(
                transfer_request_id=transfer_request,
                accepting_company=candidate_and_expected_coordinator,
            )
        )
        self.assertCompanyHasCoordinatedCooperation(
            candidate_and_expected_coordinator, cooperation
        )

    def test_after_accepting_the_candidate_is_current_coordinator_of_cooperation(
        self,
    ) -> None:
        present_coordinator = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=present_coordinator
        )
        candidate_and_expected_coordinator = self.company_generator.create_company()

        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=present_coordinator,
            cooperation=cooperation,
            candidate=candidate_and_expected_coordinator,
        )
        self.use_case.accept_coordination_transfer(
            request=AcceptCoordinationTransferUseCase.Request(
                transfer_request_id=transfer_request,
                accepting_company=candidate_and_expected_coordinator,
            )
        )
        self.assertCompanyIsCurrentCoordinatorOfCooperation(
            candidate_and_expected_coordinator, cooperation
        )

    def create_use_case_request(self) -> AcceptCoordinationTransferUseCase.Request:
        coordinator = self.company_generator.create_company()
        candidate_and_accepting_company = self.company_generator.create_company()
        transfer_request_id = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=coordinator,
            cooperation=self.cooperation_generator.create_cooperation(
                coordinator=coordinator
            ),
            candidate=candidate_and_accepting_company,
        )
        return AcceptCoordinationTransferUseCase.Request(
            transfer_request_id=transfer_request_id,
            accepting_company=candidate_and_accepting_company,
        )

    def assertCompanyHasCoordinatedCooperation(
        self, company: UUID, cooperation: UUID
    ) -> None:
        list_coordinations_response = (
            self.list_coordinations_use_case.list_coordinations(
                ListCoordinationsOfCooperationUseCase.Request(cooperation=cooperation)
            )
        )
        coordinations = list_coordinations_response.coordinations
        coordinators = [c.coordinator_id for c in coordinations]
        self.assertIn(company, coordinators)

    def assertCompanyIsCurrentCoordinatorOfCooperation(
        self, company: UUID, cooperation: UUID
    ) -> None:
        get_coop_summary_response = self.get_coop_summary_use_case(
            GetCoopSummaryRequest(requester_id=uuid4(), coop_id=cooperation)
        )
        self.assertEqual(get_coop_summary_response.current_coordinator, company)
