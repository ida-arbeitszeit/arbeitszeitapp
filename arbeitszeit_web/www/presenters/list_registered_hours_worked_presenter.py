from dataclasses import dataclass

from arbeitszeit.interactors import list_registered_hours_worked
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter


@dataclass
class RegisteredHoursWorked:
    hours: str
    worker_name: str
    worker_id: str
    registered_on: str


@dataclass
class ViewModel:
    registered_hours_worked: list[RegisteredHoursWorked]


@dataclass
class ListRegisteredHoursWorkedPresenter:
    datetime_formatter: DatetimeFormatter

    def present(self, response: list_registered_hours_worked.Response) -> ViewModel:
        registered_hours_worked = [
            RegisteredHoursWorked(
                hours=str(round(record.hours, 2)),
                worker_name=record.worker_name,
                worker_id=str(record.worker_id),
                registered_on=self.datetime_formatter.format_datetime(
                    date=record.registered_on,
                    fmt="%d.%m.%Y %H:%M",
                ),
            )
            for record in response.registered_hours_worked
        ]
        return ViewModel(registered_hours_worked=registered_hours_worked)
