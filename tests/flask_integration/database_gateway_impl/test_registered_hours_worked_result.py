from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.use_cases import register_hours_worked

from ..flask import FlaskTestCase


class RegisteredHoursWorkedResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_hours_worked_use_case = self.injector.get(
            register_hours_worked.RegisterHoursWorked
        )

    def test_get_registered_hours_worked_yields_empty_result_before_any_records_were_created(
        self,
    ) -> None:
        assert not self.database_gateway.get_registered_hours_worked()

    def test_get_registered_hours_worked_yields_non_empty_result_after_creating_a_record(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert self.database_gateway.get_registered_hours_worked()

    def test_that_record_has_correct_member_id(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.member == worker

    def test_that_record_has_correct_company_id(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.company == company

    def test_that_record_has_consistent_uuid(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker, hours=Decimal(5))
        assert (
            first_result := self.database_gateway.get_registered_hours_worked().first()
        )
        assert (
            second_result := self.database_gateway.get_registered_hours_worked().first()
        )
        assert first_result.id == second_result.id

    @parameterized.expand(
        [
            Decimal(1),
            Decimal(99),
        ]
    )
    def test_that_record_has_specified_amount(self, expected_hours: Decimal) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker, hours=expected_hours)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.amount == expected_hours

    @parameterized.expand(
        [
            datetime(2000, 1, 1),
            datetime(2000, 1, 2),
            datetime(2012, 3, 21),
        ]
    )
    def test_that_record_has_specified_registration_time(
        self, expected_time: datetime
    ) -> None:
        self.datetime_service.freeze_time(expected_time)
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.registered_on == expected_time

    def test_that_transaction_id_exists_in_db(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.transaction in (
            record.id for record in self.database_gateway.get_transactions()
        )

    def test_that_we_find_a_record_if_we_filter_by_company_where_the_hours_were_worked(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (
            self.database_gateway.get_registered_hours_worked()
            .at_company(company)
            .first()
        )

    def test_that_we_dont_find_a_record_if_we_filter_by_company_that_does_not_exist(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (
            not self.database_gateway.get_registered_hours_worked()
            .at_company(uuid4())
            .first()
        )

    def test_that_entries_are_ordered_descendingly_if_so_requested(self) -> None:
        self.datetime_service.freeze_time()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        self.datetime_service.advance_time()
        self.register_hours_worked(company=company, worker=worker)
        records = list(
            self.database_gateway.get_registered_hours_worked().ordered_by_registration_time(
                is_ascending=False
            )
        )
        assert records[0].registered_on > records[1].registered_on

    def test_that_entries_are_ordered_ascendingly_if_so_requested(self) -> None:
        self.datetime_service.freeze_time()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        self.datetime_service.advance_time()
        self.register_hours_worked(company=company, worker=worker)
        records = list(
            self.database_gateway.get_registered_hours_worked().ordered_by_registration_time(
                is_ascending=True
            )
        )
        assert records[0].registered_on < records[1].registered_on

    @parameterized.expand(
        [
            ("name1",),
            ("other name",),
        ]
    )
    def test_that_result_joined_with_worker_has_correct_worker_name(
        self, expected_name: str
    ) -> None:
        worker = self.member_generator.create_member(name=expected_name)
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (
            result := self.database_gateway.get_registered_hours_worked()
            .joined_with_worker()
            .first()
        )
        assert result[1].name == expected_name

    def test_that_result_joined_with_worker_has_correct_worker_id(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (
            result := self.database_gateway.get_registered_hours_worked()
            .joined_with_worker()
            .first()
        )
        assert result[1].id == worker

    def test_that_we_can_filter_by_id(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker, hours=Decimal(10))
        self.register_hours_worked(company=company, worker=worker, hours=Decimal(5))
        records = list(self.database_gateway.get_registered_hours_worked())
        self.assertEqual(len(records), 2)
        result = (
            self.database_gateway.get_registered_hours_worked()
            .with_id(records[0].id)
            .first()
        )
        self.assertEqual(records[0], result)

    def test_that_no_record_is_returned_when_filter_by_random_id(self) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker, hours=Decimal(10))
        self.assertIsNone(
            self.database_gateway.get_registered_hours_worked().with_id(uuid4()).first()
        )

    def register_hours_worked(
        self, company: UUID, worker: UUID, hours: Decimal = Decimal(1)
    ) -> None:
        request = register_hours_worked.RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=worker,
            hours_worked=hours,
        )
        response = self.register_hours_worked_use_case(use_case_request=request)
        assert not response.is_rejected
