from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.query_plans import QueryPlansPresenter

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl
from .url_index import (
    CompanySummaryUrlIndex,
    CoopSummaryUrlIndexTestImpl,
    PlanSummaryUrlIndexTestImpl,
)

RESPONSE_WITHOUT_RESULTS = PlanQueryResponse(results=[])
RESPONSE_WITH_ONE_RESULT = PlanQueryResponse(
    results=[
        QueriedPlan(
            plan_id=uuid4(),
            company_name="Planner name",
            company_id=uuid4(),
            product_name="Bread",
            description="For eating",
            price_per_unit=Decimal(5),
            is_public_service=False,
            is_available=True,
            is_cooperating=False,
        )
    ]
)

RESPONSE_WITH_ONE_COOPERATING_RESULT = PlanQueryResponse(
    results=[
        QueriedPlan(
            plan_id=uuid4(),
            company_name="Planner name",
            company_id=uuid4(),
            product_name="Bread",
            description="For eating",
            price_per_unit=Decimal(5),
            is_public_service=False,
            is_available=True,
            is_cooperating=True,
        )
    ]
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
        presentation = self.presenter.present(RESPONSE_WITHOUT_RESULTS)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertTrue(presentation.show_results)

    def test_show_warning_when_no_results_are_found(self):
        self.presenter.present(RESPONSE_WITHOUT_RESULTS)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_warning_when_results_are_found(self):
        self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertFalse(self.notifier.warnings)

    def test_plan_url(self) -> None:
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        plan_id = RESPONSE_WITH_ONE_RESULT.results[0].plan_id
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.plan_summary_url,
            self.plan_url_index.get_plan_summary_url(plan_id),
        )

    def test_company_name(self) -> None:
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.company_name, RESPONSE_WITH_ONE_RESULT.results[0].company_name
        )

    def test_no_coop_is_shown_with_one_non_cooperating_plan(self) -> None:
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            False,
        )

    def test_coop_is_shown_with_one_cooperating_plan(self) -> None:
        presentation = self.presenter.present(RESPONSE_WITH_ONE_COOPERATING_RESULT)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            True,
        )
