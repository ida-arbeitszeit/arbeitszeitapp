from datetime import datetime
from typing import Optional
from uuid import UUID

from arbeitszeit.records import CoordinationTenure
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.data_generators import CompanyGenerator, CooperationGenerator
from tests.flask_integration.flask import FlaskTestCase


class CoordinationTenureResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db_gateway = self.injector.get(DatabaseGatewayImpl)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_that_a_priori_no_coordination_tenures_are_in_db(self) -> None:
        coordination_tenures = self.db_gateway.get_coordination_tenures()
        assert not coordination_tenures

    def test_that_there_is_at_least_one_coordination_tenure_after_creating_one(
        self,
    ) -> None:
        self.db_gateway.create_coordination_tenure(
            company=self.company_generator.create_company(),
            cooperation=self.cooperation_generator.create_cooperation(),
            start_date=datetime(2000, 1, 1),
        )
        coordination_tenures = self.db_gateway.get_coordination_tenures()
        assert coordination_tenures

    def test_that_created_coordination_tenure_has_correct_properties_assigned(
        self,
    ) -> None:
        expected_company = self.company_generator.create_company()
        expected_cooperation = self.cooperation_generator.create_cooperation()
        expected_start_date = datetime(2345, 1, 12)
        coordination_tenure = self.db_gateway.create_coordination_tenure(
            company=expected_company,
            cooperation=expected_cooperation,
            start_date=expected_start_date,
        )
        assert coordination_tenure.company == expected_company
        assert coordination_tenure.cooperation == expected_cooperation
        assert coordination_tenure.start_date == expected_start_date

    def test_that_freshly_created_coordination_tenure_can_be_queried_by_id(
        self,
    ) -> None:
        coordination_tenure = self.create_coordination_tenure()
        coordination_tenures = self.db_gateway.get_coordination_tenures()
        assert coordination_tenures.with_id(coordination_tenure.id)

    def test_that_results_filtered_by_id_dont_contain_coordination_tenures_with_different_id(
        self,
    ) -> None:
        coordination_tenure = self.create_coordination_tenure()
        other_coordination_tenure = self.create_coordination_tenure()
        coordination_tenures = self.db_gateway.get_coordination_tenures()
        assert other_coordination_tenure not in list(
            coordination_tenures.with_id(coordination_tenure.id)
        )

    def create_coordination_tenure(self) -> CoordinationTenure:
        return self.db_gateway.create_coordination_tenure(
            company=self.company_generator.create_company(),
            cooperation=self.cooperation_generator.create_cooperation(),
            start_date=datetime(2000, 1, 1),
        )


class CoordinationsOfCooperationTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db_gateway = self.injector.get(DatabaseGatewayImpl)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_results_filtered_by_cooperation_dont_include_coordinations_of_other_cooperation(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        other_cooperation = self.cooperation_generator.create_cooperation()
        coordination_tenure = self.create_coordination_tenure(cooperation)
        other_coordination_tenure = self.create_coordination_tenure(other_cooperation)
        coordination_tenures = self.db_gateway.get_coordination_tenures()
        assert coordination_tenure in list(
            coordination_tenures.of_cooperation(cooperation)
        )
        assert other_coordination_tenure not in list(
            coordination_tenures.of_cooperation(cooperation)
        )

    def create_coordination_tenure(
        self, cooperation: Optional[UUID] = None
    ) -> CoordinationTenure:
        if cooperation is None:
            cooperation = self.cooperation_generator.create_cooperation()
        return self.db_gateway.create_coordination_tenure(
            company=self.company_generator.create_company(),
            cooperation=cooperation,
            start_date=datetime(2000, 1, 1),
        )


class JoinedWithCoordinatorTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db_gateway = self.injector.get(DatabaseGatewayImpl)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_that_joining_with_coordinator_returns_coordinator(
        self,
    ) -> None:
        expected_coordinator = self.company_generator.create_company()
        coordination_tenure = self.db_gateway.create_coordination_tenure(
            company=expected_coordinator,
            cooperation=self.cooperation_generator.create_cooperation(),
            start_date=datetime(2000, 1, 1),
        )
        self.assertTrue(
            self.companyIsCoordinatorOfCoordination(
                company=expected_coordinator, coordination_tenure=coordination_tenure.id
            )
        )

    def companyIsCoordinatorOfCoordination(
        self, company: UUID, coordination_tenure: UUID
    ) -> bool:
        coordination_tenure_and_coordinator = (
            self.db_gateway.get_coordination_tenures()
            .with_id(coordination_tenure)
            .joined_with_coordinator()
            .first()
        )
        assert coordination_tenure_and_coordinator
        _, coordinator = coordination_tenure_and_coordinator
        return coordinator.id == company
