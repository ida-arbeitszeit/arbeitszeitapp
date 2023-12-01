from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit.use_cases.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsUseCase as UseCase,
)
from tests.use_cases.base_test_case import BaseTestCase


class GetTransferRequestDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.accept_transfer_use_case = self.injector.get(
            AcceptCoordinationTransferUseCase
        )

    def test_use_case_returns_none_when_transfer_request_does_not_exists(self):
        request = UseCase.Request(coordination_transfer_request=uuid4())
        response = self.use_case.get_details(request)
        self.assertIsNone(response)

    def test_use_case_returns_correct_request_date_that_is_time_of_request_creation(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        expected_date = datetime(2020, 1, 4)
        self.datetime_service.freeze_time(expected_date)
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester, coordinator=coordinator, cooperation=cooperation
            )
        )
        assert response
        self.assertEqual(expected_date, response.request_date)

    def test_use_case_returns_cooperation_id_of_the_cooperation_that_belongs_to_request(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester,
                coordinator=coordinator,
                cooperation=cooperation,
            )
        )
        assert response
        self.assertEqual(cooperation, response.cooperation_id)

    def test_use_case_returns_cooperation_name_of_the_cooperation_that_belongs_to_request(
        self,
    ) -> None:
        expected_name = "Test Cooperation"

        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator, name=expected_name
        )
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester,
                coordinator=coordinator,
                cooperation=cooperation,
            )
        )
        assert response
        self.assertEqual(expected_name, response.cooperation_name)

    def test_use_case_returns_the_id_of_the_candidate(self) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = self.company_generator.create_company()
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester,
                coordinator=coordinator,
                cooperation=cooperation,
                candidate=candidate,
            )
        )
        assert response
        self.assertEqual(candidate, response.candidate_id)

    def test_use_case_returns_the_name_of_the_candidate(self) -> None:
        expected_name = "Test Candidate"

        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = self.company_generator.create_company(name=expected_name)
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester,
                coordinator=coordinator,
                cooperation=cooperation,
                candidate=candidate,
            )
        )
        assert response
        self.assertEqual(expected_name, response.candidate_name)

    def test_request_is_shown_as_pending_if_it_has_not_been_accepted_yet(self) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        response = self.use_case.get_details(
            self.use_case_request(
                requester=requester, coordinator=coordinator, cooperation=cooperation
            )
        )
        assert response
        self.assertTrue(response.request_is_pending)

    def test_request_is_shown_as_not_pending_if_it_has_been_accepted(self) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = self.company_generator.create_company()
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester,
            coordinator=coordinator,
            cooperation=cooperation,
            candidate=candidate,
        )
        self.accept_transfer_use_case.accept_coordination_transfer(
            AcceptCoordinationTransferUseCase.Request(
                transfer_request_id=transfer_request,
                accepting_company=candidate,
            )
        )
        response = self.use_case.get_details(
            UseCase.Request(coordination_transfer_request=transfer_request)
        )
        assert response
        self.assertFalse(response.request_is_pending)

    def use_case_request(
        self,
        requester: UUID,
        coordinator: UUID,
        cooperation: UUID,
        candidate: Optional[UUID] = None,
    ) -> UseCase.Request:
        if candidate is None:
            candidate = self.company_generator.create_company()
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester,
            coordinator=coordinator,
            cooperation=cooperation,
            candidate=candidate,
        )
        return UseCase.Request(coordination_transfer_request=transfer_request)
