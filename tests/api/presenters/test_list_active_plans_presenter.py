from tests.api.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedPlanGenerator


class TestGetPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)
