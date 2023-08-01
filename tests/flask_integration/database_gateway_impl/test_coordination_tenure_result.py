from datetime import datetime
from typing import Optional
from uuid import UUID

from arbeitszeit import entities
from tests.data_generators import CompanyGenerator, CooperationGenerator
from tests.datetime_service import FakeDatetimeService
from tests.flask_integration.flask import FlaskTestCase


class CoordinationTenureResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_there_are_no_coordination_tenures_by_default(self) -> None:
        tenures = self.database_gateway.get_coordination_tenures()
        assert not tenures

    def test_there_is_one_coordination_tenure_if_one_cooperation_has_been_created(
        self,
    ) -> None:
        self.cooperation_generator.create_cooperation()
        tenures = self.database_gateway.get_coordination_tenures()
        assert len(tenures) == 1

    def test_there_are_two_coordinations_if_one_cooperation_and_one_new_tenure_are_created(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        self.create_tenure(cooperation=coop.id)
        tenures = self.database_gateway.get_coordination_tenures()
        assert len(tenures) == 2

    def test_correct_properties_are_assigned_to_newly_created_coordination_tenure(
        self,
    ) -> None:
        expected_company = self.company_generator.create_company()
        expected_cooperation = self.cooperation_generator.create_cooperation()
        expected_date = datetime(2001, 1, 1)
        self.datetime_service.freeze_time(expected_date)
        tenure = self.database_gateway.create_coordination_tenure(
            company=expected_company,
            cooperation=expected_cooperation.id,
            start_date=expected_date,
        )
        assert tenure.company == expected_company
        assert tenure.cooperation == expected_cooperation.id
        assert tenure.start_date == expected_date

    def create_tenure(
        self, cooperation: UUID, company: Optional[UUID] = None
    ) -> entities.CoordinationTenure:
        if company is None:
            company = self.company_generator.create_company()
        tenure = self.database_gateway.create_coordination_tenure(
            company=company,
            cooperation=cooperation,
            start_date=self.datetime_service.now(),
        )
        return tenure
