from uuid import uuid4

from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE
from arbeitszeit_web.presenters.query_companies_presenter import QueryCompaniesPresenter
from arbeitszeit_web.session import UserRole
from tests.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedCompanyGenerator
from tests.presenters.url_index import UrlIndexTestImpl
from tests.session import FakeSession

from .notifier import NotifierTestImpl


class QueryCompaniesPresenterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.queried_company_generator = self.injector.get(QueriedCompanyGenerator)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.presenter = self.injector.get(QueryCompaniesPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.session = self.injector.get(FakeSession)
        self.session.login_member(uuid4())

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_pagination(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.pagination.is_visible)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        response = self.queried_company_generator.get_response()
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_results)

    def test_show_notification_when_no_results_are_found(self):
        response = self.queried_company_generator.get_response(queried_companies=[])
        self.presenter.present(response)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_notifications_when_results_are_found(self):
        response = self.queried_company_generator.get_response()
        self.presenter.present(response)
        self.assertFalse(self.notifier.warnings)

    def test_correct_company_url_is_shown(self) -> None:
        expected_company = self.queried_company_generator.get_company()
        expected_url = self.url_index.get_company_summary_url(
            user_role=UserRole.member, company_id=expected_company.company_id
        )
        response = self.queried_company_generator.get_response([expected_company])
        view_model = self.presenter.present(response)
        url = view_model.results.rows[0].company_summary_url
        self.assertEqual(url, expected_url)

    def test_correct_company_name_is_shown(self) -> None:
        expected_name = "Company XYZ"
        expected_company = self.queried_company_generator.get_company(
            name=expected_name
        )
        response = self.queried_company_generator.get_response([expected_company])
        view_model = self.presenter.present(response)
        name = view_model.results.rows[0].company_name
        self.assertEqual(name, expected_name)


class PaginationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_company_generator = self.injector.get(QueriedCompanyGenerator)
        self.presenter = self.injector.get(QueryCompaniesPresenter)

    def test_that_with_only_1_company_in_response_no_page_links_are_returned(
        self,
    ) -> None:
        response = self.queried_company_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_sufficient_companies_in_response_the_pagination_is_visible(
        self,
    ) -> None:
        companies_count = DEFAULT_PAGE_SIZE + 1
        response = self.queried_company_generator.get_response(
            total_results=companies_count
        )
        view_model = self.presenter.present(response)
        assert view_model.pagination.is_visible
