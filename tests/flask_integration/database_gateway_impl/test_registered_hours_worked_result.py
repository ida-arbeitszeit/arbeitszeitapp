from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_utc

from ..flask import FlaskTestCase


class RegisteredHoursWorkedResultTests(FlaskTestCase):
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
            datetime_utc(2000, 1, 1),
            datetime_utc(2000, 1, 2),
            datetime_utc(2012, 3, 21),
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

    def test_that_transfer_of_work_certificates_id_exists_in_db(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.transfer_of_work_certificates in (
            record.id for record in self.database_gateway.get_transfers()
        )

    def test_that_transfer_of_taxes_id_exists_in_db(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self.register_hours_worked(company=company, worker=worker)
        assert (record := self.database_gateway.get_registered_hours_worked().first())
        assert record.transfer_of_taxes in (
            record.id for record in self.database_gateway.get_transfers()
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

    def test_that_result_joined_with_transfer_of_work_certificates_has_correct_debit_account_type(
        self,
    ) -> None:
        worker_id = self.member_generator.create_member()
        company = self.company_generator.create_company_record(workers=[worker_id])
        self.register_hours_worked(company=company.id, worker=worker_id)
        assert (
            result := self.database_gateway.get_registered_hours_worked()
            .joined_with_transfer_of_work_certificates()
            .first()
        )
        assert result[1].debit_account == company.work_account

    def test_that_result_joined_with_transfer_of_work_certificates_has_correct_credit_account_type(
        self,
    ) -> None:
        worker_id = self.member_generator.create_member()
        worker = self.database_gateway.get_members().with_id(worker_id).first()
        assert worker
        company = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(company=company, worker=worker_id)
        assert (
            result := self.database_gateway.get_registered_hours_worked()
            .joined_with_transfer_of_work_certificates()
            .first()
        )
        assert result[1].credit_account == worker.account

    @parameterized.expand(
        [
            (Decimal(12),),
            (Decimal(123.1),),
        ]
    )
    def test_that_result_joined_with_transfer_of_work_certificates_has_correct_value(
        self,
        expected_value: Decimal,
    ) -> None:
        worker_id = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker_id])
        self.register_hours_worked(
            company=company, worker=worker_id, hours=expected_value
        )
        assert (
            result := self.database_gateway.get_registered_hours_worked()
            .joined_with_transfer_of_work_certificates()
            .first()
        )
        self.assertAlmostEqual(result[1].value, expected_value)

    def register_hours_worked(
        self, company: UUID, worker: UUID, hours: Decimal = Decimal(1)
    ) -> None:
        self.registered_hours_worked_generator.register_hours_worked(
            company=company,
            worker=worker,
            hours=hours,
        )
