from datetime import datetime, timedelta
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
)
from tests.use_cases.base_test_case import BaseTestCase


class ListCoordinationsOfCooperationTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListCoordinationsOfCooperationUseCase)

    def test_assertion_error_is_raised_when_trying_to_get_coordinations_of_nonexisting_cooperation(
        self,
    ) -> None:
        with self.assertRaises(AssertionError):
            self.use_case.list_coordinations(self.create_use_case_request(coop=uuid4()))

    def test_there_is_one_coordination_returned_when_a_cooperation_has_been_created(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        response = self.use_case.list_coordinations(
            self.create_use_case_request(coop=coop.id)
        )
        assert len(response.coordinations) == 1

    def test_there_is_still_only_one_coordination_returned_per_cooperation_when_two_cooperation_have_been_created(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.cooperation_generator.create_cooperation()
        response = self.use_case.list_coordinations(
            self.create_use_case_request(coop=coop.id)
        )
        assert len(response.coordinations) == 1

    def test_that_coordination_info_shows_correct_name_of_coordinator(self) -> None:
        expected_name = "Coordinator Coop."
        coordinator = self.company_generator.create_company(name=expected_name)
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        response = self.use_case.list_coordinations(
            self.create_use_case_request(coop=coop.id)
        )
        assert response.coordinations[0].coordinator_name == expected_name

    def test_that_coordination_info_shows_correct_id_of_coordinator(self) -> None:
        coordinator = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        response = self.use_case.list_coordinations(
            self.create_use_case_request(coop=coop.id)
        )
        assert response.coordinations[0].coordinator_id == coordinator

    def test_that_coordination_info_shows_correct_start_time_of_coordination_tenure(
        self,
    ) -> None:
        expected_time = datetime(2021, 10, 5, 10)
        self.datetime_service.freeze_time(expected_time)
        coop = self.cooperation_generator.create_cooperation()
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.use_case.list_coordinations(
            self.create_use_case_request(coop=coop.id)
        )
        assert response.coordinations[0].start_time == expected_time

    def create_use_case_request(
        self, coop: UUID
    ) -> ListCoordinationsOfCooperationUseCase.Request:
        return ListCoordinationsOfCooperationUseCase.Request(cooperation=coop)
