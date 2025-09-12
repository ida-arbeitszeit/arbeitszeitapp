from datetime import datetime
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    CoordinationInfo,
    ListCoordinationsOfCooperationUseCase,
)
from arbeitszeit_web.www.presenters.list_coordinations_of_cooperation_presenter import (
    ListCoordinationsOfCooperationPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class ListCoordinationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListCoordinationsOfCooperationPresenter)

    def test_presenter_shows_correct_cooperation_name(self) -> None:
        expected_cooperation_name = "Some coop test name"
        response = self.get_use_case_response_with_one_coordination(
            cooperation_name=expected_cooperation_name
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(view_model.cooperation_name, expected_cooperation_name)

    def test_presenter_shows_correct_cooperation_url(self) -> None:
        expected_cooperation = uuid4()
        expected_url = self.url_index.get_coop_summary_url(coop_id=expected_cooperation)
        response = self.get_use_case_response_with_one_coordination(
            cooperation_id=expected_cooperation
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(view_model.cooperation_url, expected_url)

    def test_presenter_shows_no_coordinations_when_use_case_response_has_none(
        self,
    ) -> None:
        response = self.get_use_case_response_with_zero_coordinations()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertFalse(view_model.has_coordinations)

    def test_presenter_shows_coordinations_when_use_case_response_has_some(
        self,
    ) -> None:
        response = self.get_use_case_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertTrue(view_model.has_coordinations)

    def test_presenter_shows_one_coordinations_when_use_case_response_has_one(
        self,
    ) -> None:
        response = self.get_use_case_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertTrue(view_model.has_coordinations)
        self.assertEqual(len(view_model.coordinations), 1)

    def test_presenter_shows_correct_coordinator_name(self) -> None:
        response = self.get_use_case_response_with_one_coordination(
            coordinator_name="fake coordinator name"
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(
            view_model.coordinations[0].coordinator_name, "fake coordinator name"
        )

    def test_presenter_shows_correct_coordinator_url(self) -> None:
        expected_coordinator = uuid4()
        expected_url = self.url_index.get_company_summary_url(
            company_id=expected_coordinator
        )
        response = self.get_use_case_response_with_one_coordination(
            coordinator_id=expected_coordinator
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(view_model.coordinations[0].coordinator_url, expected_url)

    def test_presenter_shows_correct_start_time(self) -> None:
        expected_start_time = datetime_utc(2020, 1, 1, 12, 0)
        expected_formatted_start_time = self.datetime_service.format_datetime(
            date=expected_start_time,
            fmt="%d.%m.%Y %H:%M",
        )
        response = self.get_use_case_response_with_one_coordination(
            start_time=expected_start_time
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(
            view_model.coordinations[0].start_time, expected_formatted_start_time
        )

    def test_presenter_shows_correct_end_time_if_coordination_has_none(self) -> None:
        response = ListCoordinationsOfCooperationUseCase.Response(
            coordinations=[
                CoordinationInfo(
                    coordinator_id=uuid4(),
                    coordinator_name="fake name",
                    start_time=datetime_utc(2020, 1, 1, 12, 0),
                    end_time=None,
                )
            ],
            cooperation_id=uuid4(),
            cooperation_name="Some coop test name",
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(view_model.coordinations[0].end_time, "-")

    def test_presenter_shows_correct_end_time_if_coordination_has_some(self) -> None:
        expected_end_time = datetime_utc(2022, 3, 10, 13, 0)
        expected_formatted_end_time = self.datetime_service.format_datetime(
            date=expected_end_time,
            fmt="%d.%m.%Y %H:%M",
        )
        response = self.get_use_case_response_with_one_coordination(
            end_time=expected_end_time
        )
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(
            view_model.coordinations[0].end_time, expected_formatted_end_time
        )

    def test_presenter_shows_correct_amount_of_navbar_items(self) -> None:
        response = self.get_use_case_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(len(view_model.navbar_items), 2)

    def test_first_navbar_item_is_correct(self) -> None:
        response = self.get_use_case_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(
            view_model.navbar_items[0].url,
            self.url_index.get_coop_summary_url(
                coop_id=response.cooperation_id,
            ),
        )
        self.assertEqual(
            view_model.navbar_items[0].text, self.translator.gettext("Cooperation")
        )

    def test_second_navbar_item_is_correct(self) -> None:
        response = self.get_use_case_response_with_one_coordination()
        view_model = self.presenter.list_coordinations_of_cooperation(response)
        self.assertEqual(view_model.navbar_items[1].url, None)
        self.assertEqual(
            view_model.navbar_items[1].text, self.translator.gettext("Coordinators")
        )

    def get_use_case_response_with_zero_coordinations(
        self,
    ) -> ListCoordinationsOfCooperationUseCase.Response:
        return ListCoordinationsOfCooperationUseCase.Response(
            coordinations=[],
            cooperation_id=uuid4(),
            cooperation_name="Some coop test name",
        )

    def get_use_case_response_with_one_coordination(
        self,
        coordinator_id: UUID = uuid4(),
        coordinator_name: str = "fake coordinator name",
        start_time: datetime = datetime_utc(2020, 1, 1, 12, 0),
        end_time: datetime = datetime_utc(2022, 3, 10, 13, 0),
        cooperation_id: UUID = uuid4(),
        cooperation_name: str = "Some coop test name",
    ) -> ListCoordinationsOfCooperationUseCase.Response:
        return ListCoordinationsOfCooperationUseCase.Response(
            coordinations=[
                CoordinationInfo(
                    coordinator_id=coordinator_id,
                    coordinator_name=coordinator_name,
                    start_time=start_time,
                    end_time=end_time,
                )
            ],
            cooperation_id=cooperation_id,
            cooperation_name=cooperation_name,
        )
