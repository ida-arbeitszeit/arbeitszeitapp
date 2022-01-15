from dataclasses import replace
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.use_cases.get_statistics import StatisticsResponse
from arbeitszeit_web.get_statistics import GetStatisticsPresenter

TESTING_RESPONSE_MODEL = StatisticsResponse(
    registered_companies_count=5,
    registered_members_count=30,
    active_plans_count=6,
    active_plans_public_count=2,
    avg_timeframe=Decimal(30.5),
    planned_work=Decimal(500.23),
    planned_resources=Decimal(400.1),
    planned_means=Decimal(215.23),
)


class GetStatisticsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = GetStatisticsPresenter()

    def test_planned_resources_hours_are_truncated_at_2_digits_after_comma(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            planned_resources=Decimal(400.13131313),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.planned_resources_hours,
            "400.13",
        )

    def test_planned_work_hours_are_truncated_at_2_digits_after_comma(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            planned_work=Decimal(523.12123123123),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.planned_work_hours,
            "523.12",
        )

    def test_planned_means_hours_are_truncated_at_2_digits_after_comma(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            planned_means=Decimal(123.12315),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.planned_means_hours,
            "123.12",
        )

    def test_registered_companies_count_is_displayed_correctly_as_number(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            registered_companies_count=6,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.registered_companies_count,
            "6",
        )

    def test_registered_members_count_is_displayed_correctly_as_number(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            registered_members_count=32,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.registered_members_count,
            "32",
        )

    def test_active_plans_count_is_displayed_correctly_as_number(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            active_plans_count=7,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.active_plans_count,
            "7",
        )

    def test_active_plans_public_count_is_displayed_correctly_as_number(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            active_plans_public_count=2,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.active_plans_public_count,
            "2",
        )

    def test_average_timeframe_days_are_truncated_at_2_digits_after_comma(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            avg_timeframe=Decimal(31.2125321),
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.average_timeframe_days,
            "31.21",
        )
