from uuid import uuid4

from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit_web.www.presenters.get_plan_details_member_presenter import (
    GetPlanDetailsMemberMemberPresenter,
)
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator


class PresenterTests(BaseTestCase):
    """
    some functionality tested in tests/presenters/test_plan_details_formatter.py
    """

    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanDetailsMemberMemberPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)

    def test_that_register_consumption_url_is_shown_correctly(self):
        PLAN_ID = uuid4()
        use_case_response = GetPlanDetailsUseCase.Response(
            plan_details=self.plan_details_generator.create_plan_details(
                plan_id=PLAN_ID
            )
        )
        view_model = self.presenter.present(use_case_response)
        self.assertEqual(
            view_model.register_private_consumption_url,
            self.url_index.get_register_private_consumption_url(
                amount=None, plan_id=PLAN_ID
            ),
        )
