from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.use_cases import list_registered_hours_worked
from arbeitszeit_web.www.presenters import list_registered_hours_worked_presenter
from tests.www.base_test_case import BaseTestCase


class ListRegisteredHoursWorkedPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(
            list_registered_hours_worked_presenter.ListRegisteredHoursWorkedPresenter
        )

    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_view_model_has_same_number_of_registered_hours_worked_as_response(
        self,
        number_of_records: int,
    ) -> None:
        registered_hours_worked = [
            self.create_registered_hours_worked() for _ in range(number_of_records)
        ]
        response = self.create_use_case_response(
            registered_hours_worked=registered_hours_worked
        )
        view_model = self.presenter.present(response)
        assert len(view_model.registered_hours_worked) == number_of_records

    @parameterized.expand(
        [
            (Decimal("0"), "0.00"),
            (Decimal("8.0"), "8.00"),
            (Decimal("8.5"), "8.50"),
            (Decimal("8.75"), "8.75"),
            (Decimal("8.123"), "8.12"),
            (Decimal("8.128"), "8.13"),
        ]
    )
    def test_decimal_hours_from_response_are_rounded_to_two_decimals_and_converted_to_strings(
        self,
        hours_in_response: Decimal,
        expected_string: str,
    ) -> None:
        registered_hours_worked = [
            self.create_registered_hours_worked(hours=hours_in_response)
        ]
        response = self.create_use_case_response(
            registered_hours_worked=registered_hours_worked
        )
        view_model = self.presenter.present(response)
        assert view_model.registered_hours_worked[0].hours == expected_string

    def test_worker_uuid_from_response_is_converted_to_string(self) -> None:
        worker_id = uuid4()
        expected_worker_id = str(worker_id)
        registered_hours_worked = [
            self.create_registered_hours_worked(worker_id=worker_id)
        ]
        response = self.create_use_case_response(
            registered_hours_worked=registered_hours_worked
        )
        view_model = self.presenter.present(response)
        assert view_model.registered_hours_worked[0].worker_id == expected_worker_id

    def test_worker_name_from_response_is_passed_as_is(self) -> None:
        worker_name = "Some Name 123"
        registered_hours_worked = [
            self.create_registered_hours_worked(worker_name=worker_name)
        ]
        response = self.create_use_case_response(
            registered_hours_worked=registered_hours_worked
        )
        view_model = self.presenter.present(response)
        assert view_model.registered_hours_worked[0].worker_name == worker_name

    def test_registered_on_from_response_is_formatted_correctly(self) -> None:
        registered_on = datetime(2021, 1, 1, 12, 0)
        expected_registered_on = self.datetime_service.format_datetime(
            date=registered_on, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
        )
        registered_hours_worked = [
            self.create_registered_hours_worked(registered_on=registered_on)
        ]
        response = self.create_use_case_response(
            registered_hours_worked=registered_hours_worked
        )
        view_model = self.presenter.present(response)
        assert (
            view_model.registered_hours_worked[0].registered_on
            == expected_registered_on
        )

    def create_registered_hours_worked(
        self,
        id_: UUID = uuid4(),
        hours: Decimal = Decimal("8.0"),
        worker_id: UUID = uuid4(),
        worker_name: str = "worker_name",
        registered_on: datetime = datetime(2021, 1, 1),
    ) -> list_registered_hours_worked.RegisteredHoursWorked:
        return list_registered_hours_worked.RegisteredHoursWorked(
            id=id_,
            hours=hours,
            worker_id=worker_id,
            worker_name=worker_name,
            registered_on=registered_on,
        )

    def create_use_case_response(
        self,
        registered_hours_worked: list[
            list_registered_hours_worked.RegisteredHoursWorked
        ],
    ) -> list_registered_hours_worked.Response:
        return list_registered_hours_worked.Response(
            registered_hours_worked=registered_hours_worked
        )
