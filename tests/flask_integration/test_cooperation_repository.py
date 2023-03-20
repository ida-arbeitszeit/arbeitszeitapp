from datetime import datetime

from arbeitszeit.entities import Cooperation
from arbeitszeit_flask.database.repositories import CooperationRepository
from tests.data_generators import CompanyGenerator, PlanGenerator

from .flask import FlaskTestCase


class CooperationRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.repo = self.injector.get(CooperationRepository)
        self.DEFAULT_CREATE_ARGUMENTS = dict(
            creation_timestamp=datetime.now(),
            name="test name",
            definition="test description",
            coordinator=self.company_generator.create_company_entity(),
        )

    def test_cooperation_can_be_created(self):
        cooperation = self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        self.assertIsInstance(cooperation, Cooperation)

    def test_cooperations_can_be_retrieved_by_their_id(self):
        expected_cooperation = self.repo.create_cooperation(
            **self.DEFAULT_CREATE_ARGUMENTS
        )
        self.assertEqual(
            expected_cooperation, self.repo.get_by_id(expected_cooperation.id)
        )

    def test_created_cooperation_has_correct_attributes(self):
        cooperation = self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        self.assertEqual(
            cooperation.creation_date,
            self.DEFAULT_CREATE_ARGUMENTS["creation_timestamp"],
        )
        self.assertEqual(
            cooperation.name,
            self.DEFAULT_CREATE_ARGUMENTS["name"],
        )
        self.assertEqual(
            cooperation.definition,
            self.DEFAULT_CREATE_ARGUMENTS["definition"],
        )
        self.assertEqual(
            cooperation.coordinator,
            self.DEFAULT_CREATE_ARGUMENTS["coordinator"],
        )

    def test_cooperation_can_be_retrieved_by_its_exact_name_and_case_insensitive(self):
        expected_cooperation = self.repo.create_cooperation(
            **self.DEFAULT_CREATE_ARGUMENTS
        )
        query = "tEsT NaMe"
        returned_cooperation = list(self.repo.get_by_name(query))[0]
        self.assertEqual(expected_cooperation, returned_cooperation)

    def test_cooperation_cannot_be_retrieved_by_part_of_name(self):
        self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        query = "test"
        self.assertFalse(list(self.repo.get_by_name(query)))

    def test_only_cooperations_coordinated_by_company_are_returned(self):
        company = self.company_generator.create_company_entity()
        expected_cooperation = self.repo.create_cooperation(
            creation_timestamp=datetime.now(),
            name="test name",
            definition="test description",
            coordinator=company,
        )
        self.repo.create_cooperation(
            creation_timestamp=datetime.now(),
            name="test name",
            definition="test description",
            coordinator=self.company_generator.create_company_entity(),
        )
        cooperations = list(
            self.repo.get_cooperations_coordinated_by_company(company.id)
        )
        self.assertEqual(len(cooperations), 1)
        self.assertIn(expected_cooperation, cooperations)

    def test_name_of_cooperation_is_returned(self):
        cooperation = self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        returned_name = self.repo.get_cooperation_name(cooperation.id)
        self.assertEqual(returned_name, "test name")

    def test_all_cooperations_are_returned(self):
        cooperation1 = self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        cooperation2 = self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        returned_coops = list(self.repo.get_all_cooperations())
        self.assertEqual(len(returned_coops), 2)
        self.assertIn(cooperation1, returned_coops)
        self.assertIn(cooperation2, returned_coops)

    def test_cooperations_are_counted(self):
        number_of_coops = 2
        for _ in range(number_of_coops):
            self.repo.create_cooperation(**self.DEFAULT_CREATE_ARGUMENTS)
        count = self.repo.count_cooperations()
        self.assertEqual(count, number_of_coops)
