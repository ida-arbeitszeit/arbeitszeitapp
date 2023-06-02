from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit_web.get_plan_summary_member import GetPlanSummaryMemberSuccessPresenter
from tests.presenters.data_generators import PlanSummaryGenerator
from tests.presenters.url_index import UrlIndexTestImpl

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    """
    some functionality tested in tests/presenters/test_plan_summary_formatter.py
    """

    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.presenter = self.injector.get(GetPlanSummaryMemberSuccessPresenter)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)

    def test_that_pay_product_url_is_shown_correctly(self):
        PLAN_ID = uuid4()
        use_case_response = GetPlanSummaryMember.Success(
            plan_summary=self.plan_summary_generator.create_plan_summary(
                plan_id=PLAN_ID
            )
        )
        view_model = self.presenter.present(use_case_response)
        self.assertEqual(
            view_model.pay_product_url,
            self.url_index.get_pay_consumer_product_url(amount=None, plan_id=PLAN_ID),
        )
