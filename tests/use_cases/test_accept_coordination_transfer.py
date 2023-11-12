from typing import Optional
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
        request = self.create_use_case_request(transfer_request_id=uuid4())
        response = self.use_case.accept_coordination_transfer(request)
        assert response.is_rejected
        self.assertTrue(
            response.rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_not_found
        )

    def test_use_case_fails_if_coordination_transfer_request_has_already_been_accepted(
        self,
    ) -> None:
        request = self.create_use_case_request(is_accepted=True)
        response = self.use_case.accept_coordination_transfer(request)
        assert response.is_rejected
        self.assertTrue(
            response.rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_closed
        )

    def test_use_case_succeeds_if_coordination_transfer_request_exists_and_is_open(
        self,
    ) -> None:
        request = self.create_use_case_request()
        response = self.use_case.accept_coordination_transfer(request)
        self.assertFalse(response.is_rejected)

    def test_after_accepting_transfer_the_candidate_is_coordinator_of_cooperation(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        candidate_and_expected_coordinator = self.company_generator.create_company()
        requesting_coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                cooperation=cooperation
            )
        )

        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requesting_coordination_tenure=requesting_coordination_tenure,
            candidate=candidate_and_expected_coordinator,
        )

        request = self.create_use_case_request(transfer_request_id=transfer_request)
        self.use_case.accept_coordination_transfer(request)
        self.assertCompanyHasCoordinatedCooperation(
            candidate_and_expected_coordinator, cooperation
        )

    def test_after_accepting_transfer_the_candidate_is_current_coordinator_of_cooperation(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        candidate_and_expected_coordinator = self.company_generator.create_company()
        requesting_coordination_tenure = (
            self.coordination_tenure_generator.create_coordination_tenure(
                cooperation=cooperation
            )
        )

        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requesting_coordination_tenure=requesting_coordination_tenure,
            candidate=candidate_and_expected_coordinator,
        )

        request = self.create_use_case_request(transfer_request_id=transfer_request)
        self.use_case.accept_coordination_transfer(request)
        self.assertCompanyIsCurrentCoordinatorOfCooperation(
            candidate_and_expected_coordinator, cooperation
        )

    def create_use_case_request(
        self, transfer_request_id: Optional[UUID] = None, is_accepted: bool = False
    ) -> AcceptCoordinationTransferUseCase.Request:
        if transfer_request_id is None:
            transfer_request_id = self.coordination_transfer_request_generator.create_coordination_transfer_request(
                is_accepted=is_accepted
            )
        return AcceptCoordinationTransferUseCase.Request(
            transfer_request_id=transfer_request_id
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
