from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.interactors.accept_coordination_transfer import (
    AcceptCoordinationTransferInteractor,
)
from arbeitszeit.interactors.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsInteractor as Interactor,
)
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class GetTransferRequestDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)
        self.accept_transfer_interactor = self.injector.get(
            AcceptCoordinationTransferInteractor
        )

    def test_interactor_returns_none_when_transfer_request_does_not_exists(self):
        request = Interactor.Request(coordination_transfer_request=uuid4())
        response = self.interactor.get_details(request)
        self.assertIsNone(response)

    def test_interactor_returns_correct_request_date_that_is_time_of_request_creation(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        expected_date = datetime_utc(2020, 1, 4)
        self.datetime_service.freeze_time(expected_date)
        response = self.interactor.get_details(
            self.interactor_request(requester=requester, cooperation=cooperation)
        )
        assert response
        self.assertEqual(expected_date, response.request_date)

    def test_interactor_returns_cooperation_id_of_the_cooperation_that_belongs_to_request(
        self,
    ) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        response = self.interactor.get_details(
            self.interactor_request(
                requester=requester,
                cooperation=cooperation,
            )
        )
        assert response
        self.assertEqual(cooperation, response.cooperation_id)

    def test_interactor_returns_cooperation_name_of_the_cooperation_that_belongs_to_request(
        self,
    ) -> None:
        expected_name = "Test Cooperation"

        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator, name=expected_name
        )
        response = self.interactor.get_details(
            self.interactor_request(
                requester=requester,
                cooperation=cooperation,
            )
        )
        assert response
        self.assertEqual(expected_name, response.cooperation_name)

    def test_interactor_returns_the_id_of_the_candidate(self) -> None:
        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = self.company_generator.create_company()
        response = self.interactor.get_details(
            self.interactor_request(
                requester=requester,
                cooperation=cooperation,
                candidate=candidate,
            )
        )
        assert response
        self.assertEqual(candidate, response.candidate_id)

    def test_interactor_returns_the_name_of_the_candidate(self) -> None:
        expected_name = "Test Candidate"

        requester = self.company_generator.create_company()
        coordinator = requester
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        candidate = self.company_generator.create_company(name=expected_name)
        response = self.interactor.get_details(
            self.interactor_request(
                requester=requester,
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
        response = self.interactor.get_details(
            self.interactor_request(requester=requester, cooperation=cooperation)
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
            cooperation=cooperation,
            candidate=candidate,
        )
        self.accept_transfer_interactor.accept_coordination_transfer(
            AcceptCoordinationTransferInteractor.Request(
                transfer_request_id=transfer_request,
                accepting_company=candidate,
            )
        )
        response = self.interactor.get_details(
            Interactor.Request(coordination_transfer_request=transfer_request)
        )
        assert response
        self.assertFalse(response.request_is_pending)

    def interactor_request(
        self,
        requester: UUID,
        cooperation: UUID,
        candidate: Optional[UUID] = None,
    ) -> Interactor.Request:
        if candidate is None:
            candidate = self.company_generator.create_company()
        transfer_request = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=requester,
            cooperation=cooperation,
            candidate=candidate,
        )
        return Interactor.Request(coordination_transfer_request=transfer_request)
