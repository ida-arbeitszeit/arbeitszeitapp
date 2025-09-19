from parameterized import parameterized

from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE, PAGE_PARAMETER_NAME
from arbeitszeit_web.www.controllers.list_transfers_controller import (
    ListTransfersController,
)
from tests.www.base_test_case import BaseTestCase


class ListTransfersControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(ListTransfersController)

    def test_that_interactor_request_has_default_limit(self) -> None:
        request = self.controller.create_interactor_request()
        assert request.limit == DEFAULT_PAGE_SIZE

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_that_offset_of_interactor_request_is_calculated_correctly(
        self,
        page: int,
    ) -> None:
        self.request.set_arg(PAGE_PARAMETER_NAME, page)
        expected_offset = (page - 1) * DEFAULT_PAGE_SIZE
        interactor_request = self.controller.create_interactor_request()
        assert interactor_request.offset == expected_offset
