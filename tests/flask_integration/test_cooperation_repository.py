from datetime import datetime
from unittest import TestCase

import arbeitszeit.repositories
from arbeitszeit.entities import Cooperation
from project.database.repositories import CooperationRepository
from tests.data_generators import CompanyGenerator

from .dependency_injection import get_dependency_injector


class CooperationRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.repo = self.injector.get(CooperationRepository)
        self.DEFAULT_CREATE_ARGUMENTS = dict(
            creation_timestamp=datetime.now(),
            name="test name",
            definition="test description",
            coordinator=self.company_generator.create_company(),
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

    def test_can_instantiate_a_repository_through_dependency_injection(self) -> None:
        instance = self.injector.get(arbeitszeit.repositories.CooperationRepository)
        self.assertIsInstance(instance, CooperationRepository)

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
