from uuid import uuid4

from arbeitszeit.use_cases import (
    CreateCooperation,
    CreateCooperationRequest,
    CreateCooperationResponse,
)

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_cooperation = self.injector.get(CreateCooperation)

    def test_creation_rejected_when_coordinator_does_not_exist(self) -> None:
        request = CreateCooperationRequest(
            coordinator_id=uuid4(), name="test name", definition="some info"
        )
        response = self.create_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        )

    def test_creation_is_rejected_when_coop_name_exists_already(self) -> None:
        self.cooperation_generator.create_cooperation(name="existing name")
        coordinator = self.company_generator.create_company()
        request = CreateCooperationRequest(
            coordinator_id=coordinator, name="existing name", definition="some info"
        )
        response = self.create_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        )

    def test_creation_is_rejected_when_coop_name_exists_with_case_variation(
        self,
    ) -> None:
        self.cooperation_generator.create_cooperation(name="ExisTing NaMe")
        coordinator = self.company_generator.create_company()
        request = CreateCooperationRequest(
            coordinator_id=coordinator, name="existing name", definition="some info"
        )
        response = self.create_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        )

    def test_creation_is_successfull(self) -> None:
        coordinator = self.company_generator.create_company()
        request = CreateCooperationRequest(
            coordinator_id=coordinator, name="test name", definition="some info"
        )
        response = self.create_cooperation(request)
        assert response
