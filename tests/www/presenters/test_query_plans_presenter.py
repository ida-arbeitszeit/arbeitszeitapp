from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.pagination import PAGE_PARAMETER_NAME
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.query_plans_presenter import QueryPlansPresenter
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import QueriedPlanGenerator


class QueryPlansPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryPlansPresenter)
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

    @parameterized.expand(
        [
            (-1,),
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_correct_number_of_total_results_is_passed_on_to_view_model(
        self,
        number_of_results: int,
    ) -> None:
        response = self.queried_plan_generator.get_response(
            total_results=number_of_results
        )
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.total_results, number_of_results)

    def test_correct_plan_url_is_shown(self) -> None:
        plan_id = uuid4()
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(plan_id=plan_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.plan_details_url,
            self.url_index.get_plan_details_url(
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
            self.url_index.get_company_summary_url(company_id=company_id),
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

    @parameterized.expand([(True,), (False,)])
    def test_that_is_expired_bool_is_passed_on_to_view_model(
        self, is_expired: bool
    ) -> None:
        response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan(is_expired=is_expired)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_expired,
            is_expired,
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

    def test_that_with_only_1_plan_in_response_no_page_links_are_returned(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_plans_in_response_the_pagination_is_visible(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert view_model.pagination.is_visible

    def test_that_with_15_plans_in_response_the_pagination_is_not_visible(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=15)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_plans_there_are_2_pages(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 2

    def test_that_with_31_plans_there_are_3_pages(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=31)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 3

    def test_that_with_30_plans_there_are_2_pages(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 2

    def test_that_label_of_first_page_is_1(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[0].label == "1"

    def test_that_label_of_second_page_is_2(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[1].label == "2"

    def test_with_requested_offset_of_0_the_first_page_is_current(self) -> None:
        response = self.queried_plan_generator.get_response(requested_offset=0)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[0].is_current

    def test_with_requested_offset_of_0_the_second_page_is_not_current(self) -> None:
        response = self.queried_plan_generator.get_response(
            requested_offset=0, total_results=30
        )
        view_model = self.presenter.present(response)
        assert not view_model.pagination.pages[1].is_current

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_that_correct_pages_are_shown_as_currently_selected(
        self,
        page_number_in_query_string: int,
    ) -> None:
        self.request.set_arg(PAGE_PARAMETER_NAME, str(page_number_in_query_string))
        response = self.queried_plan_generator.get_response(total_results=100)
        view_model = self.presenter.present(response)
        for index, page in enumerate(view_model.pagination.pages):
            if index == page_number_in_query_string - 1:
                assert page.is_current
            else:
                assert not page.is_current

    def test_that_page_links_generated_contain_page_number_in_query_args(self) -> None:
        response = self.queried_plan_generator.get_response(total_results=45)
        view_model = self.presenter.present(response)
        for n, page in enumerate(view_model.pagination.pages):
            self._assertQueryArg(page.href, name="page", value=str(n + 1))

    def test_that_other_query_arguments_are_preserved_when_generating_page_links(
        self,
    ) -> None:
        expected_name = "name123"
        expected_value = "value123"
        self.request.set_arg(expected_name, expected_value)
        response = self.queried_plan_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        self._assertQueryArg(
            view_model.pagination.pages[0].href,
            name=expected_name,
            value=expected_value,
        )

    def test_that_page_links_lead_to_same_scheme_and_domain_as_original_page(
        self,
    ) -> None:
        expected_url = "url://some_url_with_pagination"
        self.request.set_request_target(expected_url)
        self.session.login_member(uuid4())
        response = self.queried_plan_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        page_url = view_model.pagination.pages[0].href
        self._assertSameUrlScheme(page_url, expected_url)
        self._assertSameUrlDomain(page_url, expected_url)

    def _assertQueryArg(self, url: str, *, name: str, value: str) -> None:
        query_args = parse_qs(urlparse(url).query)
        assert name in query_args, f"Value for {name} was not found in query of {url}"
        assert (
            len(query_args[name]) == 1
        ), f"More the one value for {name} found in query args of {url}"
        assert (
            query_args[name][0] == value
        ), f"For query argument {name} expected {value} but found {query_args[name][0]}"

    def _assertSameUrlScheme(self, first: str, second: str) -> None:
        first_scheme = urlparse(first).scheme
        second_scheme = urlparse(second).scheme
        assert first_scheme == second_scheme

    def _assertSameUrlDomain(self, first: str, second: str) -> None:
        first_domain = urlparse(first).netloc
        second_domain = urlparse(second).netloc
        assert first_domain == second_domain
