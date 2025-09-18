from arbeitszeit_web.api.presenters.interfaces import JsonObject
from arbeitszeit_web.api.presenters.query_companies_api_presenter import (
    QueryCompaniesApiPresenter,
)
from tests.api.presenters.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import QueriedCompanyGenerator


class TestViewModelCreation(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryCompaniesApiPresenter)
        self.queried_company_generator = self.injector.get(QueriedCompanyGenerator)

    def test_presenter_shows_limit_as_None_when_no_limit_was_requested(self):
        interactor_response = self.queried_company_generator.get_response(
            requested_limit=None, requested_offset=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertIsNone(view_model.limit)

    def test_presenter_shows_offset_as_None_when_no_offset_was_requested(self):
        interactor_response = self.queried_company_generator.get_response(
            requested_offset=None, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertIsNone(view_model.offset)

    def test_view_model_shows_requested_offset(self):
        interactor_response = self.queried_company_generator.get_response(
            queried_companies=[], requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(view_model.offset, 5)

    def test_view_model_shows_requested_limit(self):
        interactor_response = self.queried_company_generator.get_response(
            queried_companies=[], requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(view_model.limit, 10)

    def test_view_model_shows_same_total_results_as_interactor(self):
        interactor_response = self.queried_company_generator.get_response(
            total_results=12, requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(view_model.total_results, 12)

    def test_view_model_has_no_results_if_interactor_response_has_no_queried_company(
        self,
    ):
        interactor_response = self.queried_company_generator.get_response(
            queried_companies=[], requested_offset=0, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(len(view_model.results), 0)

    def test_view_model_has_one_result_if_interactor_response_has_one_queried_company(
        self,
    ):
        company = self.queried_company_generator.get_company()
        interactor_response = self.queried_company_generator.get_response(
            queried_companies=[company], requested_offset=0, requested_limit=10
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(len(view_model.results), 1)


class TestSchema(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_company_generator = self.injector.get(QueriedCompanyGenerator)
        self.presenter = self.injector.get(QueryCompaniesApiPresenter)

    def test_schema_top_level(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        assert schema.name == "CompanyList"
