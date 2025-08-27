from datetime import datetime
from decimal import Decimal
from typing import Optional

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases.list_transfers import ListTransfersUseCase, Request
from tests.use_cases.base_test_case import BaseTestCase


class ListTransfersTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListTransfersUseCase)

    def test_that_empty_list_is_returned_if_no_transfers_exist(self) -> None:
        response = self.use_case.list_transfers(_create_request())
        assert not response.transfers

    def test_that_original_request_is_returned(self) -> None:
        request = _create_request()
        response = self.use_case.list_transfers(request)
        assert response.request == request


class LimitAndOffsetTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListTransfersUseCase)

    @parameterized.expand(
        [
            (None, None, 3),
            (3, None, 3),
            (3, 0, 3),
            (1, 0, 1),
            (2, 0, 2),
            (3, 2, 1),
            (3, 1, 2),
        ]
    )
    def test_that_limit_and_offset_are_applied_correctly_when_there_are_three_transfers_in_the_system(
        self, limit: int, offset: int, expected_results: int
    ) -> None:
        self.plan_generator.create_plan()
        request = _create_request(limit=limit, offset=offset)
        response = self.use_case.list_transfers(request)
        assert response.total_results == 3
        assert len(response.transfers) == expected_results


class ListTransfersOfApprovedProductivePlanTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListTransfersUseCase)

    def test_that_three_transfers_are_returned_after_approval_of_plan(self) -> None:
        self.plan_generator.create_plan()
        response = self.use_case.list_transfers(_create_request())
        assert len(response.transfers) == 3
        assert response.total_results == 3

    def test_that_six_transfers_are_returned_after_approval_of_two_plans(self) -> None:
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        response = self.use_case.list_transfers(_create_request())
        assert len(response.transfers) == 6
        assert response.total_results == 6

    def test_that_all_transfers_have_correct_date(self) -> None:
        expected_date = datetime(2024, 1, 1, 12, 0)
        self.datetime_service.freeze_time(expected_date)
        self.plan_generator.create_plan()
        response = self.use_case.list_transfers(_create_request())
        assert all(transfer.date == expected_date for transfer in response.transfers)

    def test_that_debit_account_is_planners_prd_account_for_all_transfers(self) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.use_case.list_transfers(_create_request())
        assert all(
            transfer.debit_account == planner.product_account
            for transfer in response.transfers
        )

    def test_that_planning_company_is_shown_as_debtor_and_creditor_for_all_transfers(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.use_case.list_transfers(_create_request())
        assert all(transfer.debtor == planner for transfer in response.transfers)
        assert all(transfer.creditor == planner for transfer in response.transfers)

    def test_that_one_of_three_transfers_is_credited_to_planners_means_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.use_case.list_transfers(_create_request())
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.means_account
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_means_account_has_correct_value_and_type(
        self, planned_means: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
                means_cost=planned_means,
            )
        )
        response = self.use_case.list_transfers(_create_request())
        assert any(
            transfer.value == planned_means
            and transfer.transfer_type == TransferType.credit_p
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_raw_materials_account_has_correct_value_and_type(
        self, planned_raw_materials: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=planned_raw_materials,
                means_cost=Decimal(0),
            )
        )
        response = self.use_case.list_transfers(_create_request())
        assert any(
            transfer.value == planned_raw_materials
            and transfer.transfer_type == TransferType.credit_r
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_work_account_has_correct_value_and_type(
        self, planned_labour: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=planned_labour,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            )
        )
        response = self.use_case.list_transfers(_create_request())
        assert any(
            transfer.value == planned_labour
            and transfer.transfer_type == TransferType.credit_a
            for transfer in response.transfers
        )

    def test_that_one_of_three_transfers_is_credited_to_planners_raw_material_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.use_case.list_transfers(_create_request())
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.raw_material_account
            for transfer in response.transfers
        )

    def test_that_one_of_three_transfers_is_credited_to_planners_work_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.use_case.list_transfers(_create_request())
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.work_account
            for transfer in response.transfers
        )

    def test_that_newest_transfer_is_returned_first(self) -> None:
        date1 = datetime(2024, 1, 1, 12, 0)
        self.datetime_service.freeze_time(date1)
        self.plan_generator.create_plan()

        date2 = datetime(2024, 1, 2, 12, 0)
        self.datetime_service.freeze_time(date2)
        self.plan_generator.create_plan()

        response = self.use_case.list_transfers(_create_request())

        assert len(response.transfers) == 6
        assert response.transfers[0].date == date2


def _create_request(
    limit: Optional[int] = None, offset: Optional[int] = None
) -> Request:
    return Request(limit=limit, offset=offset)
