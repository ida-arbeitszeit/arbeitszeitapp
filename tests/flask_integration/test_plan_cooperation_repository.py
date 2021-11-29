from datetime import datetime
from typing import List
from unittest import TestCase

from arbeitszeit.entities import Plan
from project.database.repositories import (
    CooperationRepository,
    PlanCooperationRepository,
    PlanRepository,
)
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


def plan_in_list(plan: Plan, plan_list: List[Plan]) -> bool:
    for p in plan_list:
        if p.id == plan.id:
            return True
    return False


class PlanCooperationRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.cooperation_repository = self.injector.get(CooperationRepository)
        self.repo = self.injector.get(PlanCooperationRepository)
        self.plan_repo = self.injector.get(PlanRepository)
        self.DEFAULT_CREATE_ARGUMENTS = dict(
            creation_timestamp=datetime.now(),
            name="test name",
            definition="test description",
            coordinator=self.company_generator.create_company(),
        )

    def test_possible_to_set_requested_cooperation_attribute(self):
        cooperation = self.cooperation_repository.create_cooperation(
            **self.DEFAULT_CREATE_ARGUMENTS
        )
        plan = self.plan_generator.create_plan()

        self.repo.set_requested_cooperation(plan.id, cooperation.id)

        plan_from_orm = self.plan_repo.get_plan_by_id(plan.id)
        self.assertTrue(plan_from_orm.requested_cooperation)

    def test_only_requesting_plans_for_cooperation_are_returned(self):
        coop = self.cooperation_repository.create_cooperation(
            **self.DEFAULT_CREATE_ARGUMENTS
        )
        requesting_plan1 = self.plan_generator.create_plan(
            activation_date=datetime.min, requested_cooperation=coop
        )
        requesting_plan2 = self.plan_generator.create_plan(
            activation_date=datetime.min, requested_cooperation=coop
        )
        self.plan_generator.create_plan(
            activation_date=datetime.min, requested_cooperation=None
        )
        requesting_plans = list(self.repo.get_requests(coop.coordinator.id))
        assert len(requesting_plans) == 2
        assert plan_in_list(requesting_plan1, requesting_plans)
        assert plan_in_list(requesting_plan2, requesting_plans)
