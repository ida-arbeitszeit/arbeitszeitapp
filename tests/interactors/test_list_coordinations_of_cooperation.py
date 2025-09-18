from datetime import timedelta
from uuid import UUID, uuid4

from arbeitszeit.interactors.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationInteractor,
)
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class ListCoordinationsOfCooperationTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListCoordinationsOfCooperationInteractor)

    def test_assertion_error_is_raised_when_trying_to_get_coordinations_of_nonexisting_cooperation(
        self,
    ) -> None:
        with self.assertRaises(AssertionError):
            self.interactor.list_coordinations(
                self.create_interactor_request(coop=uuid4())
            )

    def test_there_is_one_coordination_returned_when_a_cooperation_has_been_created(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 1

    def test_there_is_still_only_one_coordination_returned_per_cooperation_when_two_cooperation_have_been_created(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.cooperation_generator.create_cooperation()
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 1

    def test_that_coordination_info_shows_correct_name_of_cooperation(self) -> None:
        expected_name = "Cooperation Coop."
        coop = self.cooperation_generator.create_cooperation(name=expected_name)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert response.cooperation_name == expected_name

    def test_that_coordination_info_shows_correct_id_of_cooperation(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert response.cooperation_id == coop

    def test_that_coordination_info_shows_correct_name_of_coordinator(self) -> None:
        expected_name = "Coordinator Coop."
        coordinator = self.company_generator.create_company(name=expected_name)
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert response.coordinations[0].coordinator_name == expected_name

    def test_that_coordination_info_shows_correct_id_of_coordinator(self) -> None:
        coordinator = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert response.coordinations[0].coordinator_id == coordinator

    def test_that_coordination_info_shows_correct_start_time_of_coordination_tenure(
        self,
    ) -> None:
        expected_time = datetime_utc(2021, 10, 5, 10)
        self.datetime_service.freeze_time(expected_time)
        coop = self.cooperation_generator.create_cooperation()
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert response.coordinations[0].start_time == expected_time

    def test_that_coordination_has_no_end_time_when_there_is_only_one_coordination(
        self,
    ) -> None:
        expected_time = datetime_utc(2021, 10, 5, 10)
        self.datetime_service.freeze_time(expected_time)
        coop = self.cooperation_generator.create_cooperation()
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 1
        assert response.coordinations[0].end_time is None

    def test_that_first_coordination_of_two_in_response_has_no_end_time(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.coordination_tenure_generator.create_coordination_tenure(cooperation=coop)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 2
        assert response.coordinations[0].end_time is None

    def test_that_second_coordination_of_two_in_response_has_correct_end_time(
        self,
    ) -> None:
        first_timestamp = datetime_utc(2021, 10, 5, 10)
        self.datetime_service.freeze_time(first_timestamp)
        coop = self.cooperation_generator.create_cooperation()
        self.datetime_service.advance_time(timedelta(days=2))
        self.coordination_tenure_generator.create_coordination_tenure(cooperation=coop)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 2
        assert response.coordinations[1].end_time == first_timestamp + timedelta(days=2)

    def test_that_of_three_coordinations_only_the_first_in_response_has_no_end_time(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.coordination_tenure_generator.create_coordination_tenure(cooperation=coop)
        self.coordination_tenure_generator.create_coordination_tenure(cooperation=coop)
        response = self.interactor.list_coordinations(
            self.create_interactor_request(coop=coop)
        )
        assert len(response.coordinations) == 3
        assert response.coordinations[0].end_time is None
        assert response.coordinations[1].end_time
        assert response.coordinations[2].end_time

    def create_interactor_request(
        self, coop: UUID
    ) -> ListCoordinationsOfCooperationInteractor.Request:
        return ListCoordinationsOfCooperationInteractor.Request(cooperation=coop)
