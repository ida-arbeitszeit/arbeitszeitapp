from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit.use_cases.get_coop_summary import (
    GetCoopSummaryRequest,
    GetCoopSummaryUseCase,
)
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
        self.get_coop_summary_use_case = self.injector.get(GetCoopSummaryUseCase)
        self.request_transfer_use_case = self.injector.get(
            RequestCoordinationTransferUseCase
        )

    def test_use_case_fails_if_coordination_transfer_request_does_not_exist(
        self,
    ) -> None:
        response = self.use_case.accept_coordination_transfer(
            self.create_use_case_request(transfer_request_id=uuid4())
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
        response = self.use_case.accept_coordination_transfer(
            self.create_use_case_request(accepting_company_is_candidate=False)
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
        candidate = self.company_generator.create_company()
        request = self.create_use_case_request(candidate=candidate)
        response = self.use_case.accept_coordination_transfer(request=request)
        self.assertCompanyHasCoordinatedCooperation(candidate, response.cooperation_id)

    def test_after_accepting_the_candidate_is_current_coordinator_of_cooperation(
        self,
    ) -> None:
        candidate = self.company_generator.create_company()
        request = self.create_use_case_request(candidate=candidate)
        response = self.use_case.accept_coordination_transfer(request=request)
        self.assertCompanyIsCurrentCoordinatorOfCooperation(
            candidate, response.cooperation_id
        )

    def test_original_coordination_transfer_id_is_returned_if_use_case_succeeds(
        self,
    ) -> None:
        request = self.create_use_case_request()
        response = self.use_case.accept_coordination_transfer(request)
        self.assertFalse(response.is_rejected)
        self.assertEqual(response.transfer_request_id, request.transfer_request_id)

    def test_original_coordination_transfer_id_is_returned_if_use_case_fails(
        self,
    ) -> None:
        response = self.use_case.accept_coordination_transfer(
            self.create_use_case_request(transfer_request_id=uuid4())
        )
        self.assertTrue(response.is_rejected)
        self.assertEqual(response.transfer_request_id, response.transfer_request_id)

    def create_use_case_request(
        self,
        transfer_request_id: Optional[UUID] = None,
        candidate: Optional[UUID] = None,
        accepting_company: Optional[UUID] = None,
        accepting_company_is_candidate: bool = True,
    ) -> AcceptCoordinationTransferUseCase.Request:
        coordinator = self.company_generator.create_company()
        if candidate is None:
            candidate = self.company_generator.create_company()
        if accepting_company is None:
            accepting_company = (
                candidate
                if accepting_company_is_candidate
                else self.company_generator.create_company()
            )
        if transfer_request_id is None:
            transfer_request_id = self.coordination_transfer_request_generator.create_coordination_transfer_request(
                requester=coordinator,
                cooperation=self.cooperation_generator.create_cooperation(
                    coordinator=coordinator
                ),
                candidate=candidate,
            )
        return AcceptCoordinationTransferUseCase.Request(
            transfer_request_id=transfer_request_id,
            accepting_company=accepting_company,
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
        get_coop_summary_response = self.get_coop_summary_use_case.execute(
            GetCoopSummaryRequest(requester_id=uuid4(), coop_id=cooperation)
        )
        self.assertEqual(get_coop_summary_response.current_coordinator, company)
