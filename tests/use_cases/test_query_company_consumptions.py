from datetime import datetime, timedelta

from arbeitszeit.use_cases.query_company_consumptions import QueryCompanyConsumptions
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_consumptions = self.injector.get(QueryCompanyConsumptions)

    def test_that_no_consumption_is_returned_when_searching_an_empty_repo(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        results = list(self.query_consumptions(company))
        assert not results

    def test_that_consumption_with_specified_plan_is_queried_after_consumption_for_this_plan_was_done(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, plan=plan
        )
        results = list(self.query_consumptions(company))
        assert len(results) == 1
        latest_consumption = results[0]
        assert latest_consumption.plan_id == plan

    def test_latter_of_two_consumptions_is_returned_first_other_one_is_returned_second(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_plan = self.plan_generator.create_plan()
        second_plan = self.plan_generator.create_plan()
        company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, plan=first_plan
        )
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company, plan=second_plan
        )
        results = list(self.query_consumptions(company))
        assert results[0].plan_id == second_plan
        assert results[1].plan_id == first_plan
