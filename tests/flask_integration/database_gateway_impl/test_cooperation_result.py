from datetime import datetime, timedelta

from arbeitszeit.entities import Cooperation
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.data_generators import (
    CompanyGenerator,
    CooperationGenerator,
    CoordinationTenureGenerator,
)
from tests.datetime_service import FakeDatetimeService

from ..flask import FlaskTestCase


class CooperationResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db_gateway = self.injector.get(DatabaseGatewayImpl)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.coordination_tenure_generator = self.injector.get(
            CoordinationTenureGenerator
        )
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_a_priori_no_cooperations_are_in_db(self) -> None:
        cooperations = self.db_gateway.get_cooperations()
        assert not cooperations

    def test_that_there_is_at_least_one_cooperation_after_creating_one(self) -> None:
        self.db_gateway.create_cooperation(
            name="",
            definition="",
            creation_timestamp=datetime(2000, 1, 1),
        )
        cooperations = self.db_gateway.get_cooperations()
        assert cooperations

    def test_that_created_cooperation_has_correct_properties_assigned(self) -> None:
        expected_name = "expected_name"
        expected_definition = "expected definition"
        expected_creation_timestamp = datetime(2345, 1, 12)
        cooperation = self.db_gateway.create_cooperation(
            name=expected_name,
            definition=expected_definition,
            creation_timestamp=expected_creation_timestamp,
        )
        assert cooperation.name == expected_name
        assert cooperation.definition == expected_definition
        assert cooperation.creation_date == expected_creation_timestamp

    def test_that_freshly_created_cooperation_can_be_queried_by_id(self) -> None:
        cooperation = self.create_cooperation()
        cooperations = self.db_gateway.get_cooperations()
        assert cooperations.with_id(cooperation.id)

    def test_that_results_filtered_by_id_dont_contain_coops_with_different_id(
        self,
    ) -> None:
        cooperation = self.create_cooperation()
        other_cooperation = self.create_cooperation()
        cooperations = self.db_gateway.get_cooperations()
        assert other_cooperation not in list(cooperations.with_id(cooperation.id))

    def test_results_filtered_by_name_include_cooperations_with_exact_match(
        self,
    ) -> None:
        expected_name = "expected coop name"
        self.create_cooperation(name=expected_name)
        cooperations = self.db_gateway.get_cooperations()
        assert cooperations.with_name_ignoring_case(expected_name)

    def test_results_filtered_by_name_dont_include_coops_where_query_is_only_a_substring(
        self,
    ) -> None:
        coop_name = "coop name"
        self.create_cooperation(name=coop_name)
        cooperations = self.db_gateway.get_cooperations()
        assert not cooperations.with_name_ignoring_case(coop_name[:-1])

    def test_results_filtered_by_name_include_coops_with_differing_case(
        self,
    ) -> None:
        coop_name = "coop name"
        self.create_cooperation(name=coop_name)
        cooperations = self.db_gateway.get_cooperations()
        assert cooperations.with_name_ignoring_case(coop_name.upper())

    def test_results_filtered_by_coordinator_includes_previously_created_coop_by_coordinator(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        self.coordination_tenure_generator.create_coordination_tenure(
            company=coordinator
        )
        cooperations = self.db_gateway.get_cooperations()
        assert cooperations.coordinated_by_company(coordinator)

    def test_results_filtered_by_coordinator_dont_include_coop_by_other_coordinator(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.coordination_tenure_generator.create_coordination_tenure(
            company=coordinator
        )
        cooperations = self.db_gateway.get_cooperations()
        assert not cooperations.coordinated_by_company(other_company)

    def test_that_joining_with_current_coordinator_yields_the_current_coordinator_of_a_coop(
        self,
    ) -> None:
        expected_coordinator_name = "test coordinator"
        coordinator_id = self.company_generator.create_company(
            name=expected_coordinator_name
        )
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator_id)
        self.datetime_service.advance_time(timedelta(days=1))
        expected_coordination = (
            self.coordination_tenure_generator.create_coordination_tenure(
                cooperation=coop.id, company=coordinator_id
            )
        )

        cooperations = self.db_gateway.get_cooperations()
        result = cooperations.joined_with_current_coordinator().first()
        assert result is not None
        _, coordinator = result
        assert coordinator.id == coordinator_id
        assert coordinator.id == expected_coordination.company
        assert coordinator.name == expected_coordinator_name

    def create_cooperation(self, name: str = "test name") -> Cooperation:
        return self.db_gateway.create_cooperation(
            name=name,
            definition="",
            creation_timestamp=datetime(2000, 1, 1),
        )
