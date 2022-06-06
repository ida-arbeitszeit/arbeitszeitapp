from decimal import Decimal
from typing import List
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.query_plans import QueryPlansPresenter

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl
from .url_index import (
    CompanySummaryUrlIndex,
    CoopSummaryUrlIndexTestImpl,
    PlanSummaryUrlIndexTestImpl,
)


class QueryPlansPresenterTests(TestCase):
    def setUp(self):
        self.injector = get_dependency_injector()
        self.plan_url_index = self.injector.get(PlanSummaryUrlIndexTestImpl)
        self.company_url_index = self.injector.get(CompanySummaryUrlIndex)
        self.coop_url_index = self.injector.get(CoopSummaryUrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.presenter = self.injector.get(QueryPlansPresenter)

    def test_presenting_empty_response_leads_to_not_showing_results(self):
        response = self._get_response([])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        response = self._get_response([self._get_queried_plan()])
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_results)

    def test_show_warning_when_no_results_are_found(self):
        response = self._get_response([])
        self.presenter.present(response)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_warning_when_results_are_found(self):
        response = self._get_response([self._get_queried_plan()])
        self.presenter.present(response)
        self.assertFalse(self.notifier.warnings)

    def test_correct_plan_url_is_shown(self) -> None:
        plan_id = uuid4()
        response = self._get_response([self._get_queried_plan(plan_id=plan_id)])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.plan_summary_url,
            self.plan_url_index.get_plan_summary_url(plan_id),
        )

    def test_correct_company_url_is_shown(self) -> None:
        company_id = uuid4()
        response = self._get_response([self._get_queried_plan(company_id=company_id)])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.company_summary_url,
            self.company_url_index.get_company_summary_url(company_id),
        )

    def test_correct_company_name_is_shown(self) -> None:
        response = self._get_response([self._get_queried_plan()])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(table_row.company_name, "Planner name")

    def test_no_coop_is_shown_with_one_non_cooperating_plan(self) -> None:
        response = self._get_response([self._get_queried_plan(is_cooperating=False)])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            False,
        )

    def test_coop_is_shown_with_one_cooperating_plan(self) -> None:
        response = self._get_response([self._get_queried_plan(is_cooperating=True)])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            True,
        )

    def test_public_service_bool_is_passed_on_to_view_model(self) -> None:
        response = self._get_response([self._get_queried_plan()])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_public_service,
            False,
        )

    def test_that_description_is_shown_without_line_returns(self) -> None:
        response = self._get_response([self._get_queried_plan()])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn("For eatingNext paragraphThird one", table_row.description)

    def test_that_only_first_few_chars_of_description_are_shown(self) -> None:
        description = "For eating\nNext paragraph\rThird one Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores."
        expected_substring = "For eatingNext paragraphThird one"
        unexpected_substring = "et accusam et justo duo dolores."
        response = self._get_response([self._get_queried_plan(description=description)])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn(expected_substring, table_row.description)
        self.assertNotIn(unexpected_substring, table_row.description)

    def _get_queried_plan(
        self,
        plan_id: UUID = None,
        company_id: UUID = None,
        is_cooperating: bool = None,
        description: str = None,
    ) -> QueriedPlan:
        if plan_id is None:
            plan_id = uuid4()
        if company_id is None:
            company_id = uuid4()
        if is_cooperating is None:
            is_cooperating = False
        if description is None:
            description = "For eating\nNext paragraph\rThird one"
        return QueriedPlan(
            plan_id=plan_id,
            company_name="Planner name",
            company_id=company_id,
            product_name="Bread",
            description=description,
            price_per_unit=Decimal(5),
            is_public_service=False,
            is_available=True,
            is_cooperating=is_cooperating,
        )

    def _get_response(self, queried_plans: List[QueriedPlan]) -> PlanQueryResponse:
        return PlanQueryResponse(results=[plan for plan in queried_plans])
