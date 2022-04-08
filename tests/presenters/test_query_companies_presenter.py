from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.query_companies import CompanyQueryResponse, QueriedCompany
from arbeitszeit_web.query_companies import QueryCompaniesPresenter

from .notifier import NotifierTestImpl

RESPONSE_WITHOUT_RESULTS = CompanyQueryResponse(results=[])
RESPONSE_WITH_ONE_RESULT = CompanyQueryResponse(
    results=[
        QueriedCompany(
            company_id=uuid4(),
            company_name="Company",
            company_email="company@cp.org",
        )
    ]
)


class QueryCompaniesPresenterTests(TestCase):
    def setUp(self):
        self.notifier = NotifierTestImpl()
        self.url_index = CompanySummaryUrlIndex()
        self.presenter = QueryCompaniesPresenter(
            user_notifier=self.notifier, company_url_index=self.url_index
        )

    def test_empty_view_model_does_not_show_results(self):
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_use_case_response_leads_to_showing_results(self):
        presentation = self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertTrue(presentation.show_results)

    def test_show_notification_when_no_results_are_found(self):
        self.presenter.present(RESPONSE_WITHOUT_RESULTS)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_notifications_when_results_are_found(self):
        self.presenter.present(RESPONSE_WITH_ONE_RESULT)
        self.assertFalse(self.notifier.warnings)


class CompanySummaryUrlIndex:
    def get_company_summary_url(self, company_id: UUID) -> str:
        return f"fake_company_url:{company_id}"
