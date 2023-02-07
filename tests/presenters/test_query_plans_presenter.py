from uuid import uuid4

from arbeitszeit_web.query_plans import QueryPlansPresenter
from arbeitszeit_web.session import UserRole
from tests.presenters.data_generators import QueriedPlanGenerator
from tests.session import FakeSession

from .base_test_case import BaseTestCase
from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl


class QueryPlansPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.presenter = self.injector.get(QueryPlansPresenter)
        self.session = self.injector.get(FakeSession)
        self.queried_plan_generator = QueriedPlanGenerator()
        self.session.login_member(uuid4())

    def test_presenting_empty_response_leads_to_not_showing_results(self) -> None:
        response = self.queried_plan_generator.get_response([])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self) -> None:
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_results)

    def test_show_warning_when_no_results_are_found(self) -> None:
        response = self.queried_plan_generator.get_response([])
        self.presenter.present(response)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_warning_when_results_are_found(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        self.presenter.present(response)
        self.assertFalse(self.notifier.warnings)

    def test_correct_plan_url_is_shown(self) -> None:
        plan_id = uuid4()
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(plan_id=plan_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.plan_summary_url,
            self.url_index.get_plan_summary_url(
                user_role=UserRole.member, plan_id=plan_id
            ),
        )

    def test_correct_company_url_is_shown(self) -> None:
        company_id = uuid4()
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(company_id=company_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.company_summary_url,
            self.url_index.get_company_summary_url(
                user_role=UserRole.member, company_id=company_id
            ),
        )

    def test_correct_company_name_is_shown(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(table_row.company_name, "Planner name")

    def test_no_coop_is_shown_with_one_non_cooperating_plan(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(is_cooperating=False)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            False,
        )

    def test_coop_is_shown_with_one_cooperating_plan(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(is_cooperating=True)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            True,
        )

    def test_public_service_bool_is_passed_on_to_view_model(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_public_service,
            False,
        )

    def test_that_description_is_shown_without_line_returns(self) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn("For eatingNext paragraphThird one", table_row.description)

    def test_that_only_first_few_chars_of_description_are_shown(self) -> None:
        description = "For eating\nNext paragraph\rThird one Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores."
        expected_substring = "For eatingNext paragraphThird one"
        unexpected_substring = "et accusam et justo duo dolores."
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(description=description)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn(expected_substring, table_row.description)
        self.assertNotIn(unexpected_substring, table_row.description)
