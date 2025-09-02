from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import Transfer
from arbeitszeit.transfers.compensation import CompensationTransferService
from arbeitszeit.transfers.transfer_type import TransferType
from tests.use_cases.base_test_case import BaseTestCase


class CompensationTransferServiceTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(CompensationTransferService)

    def test_no_compensation_transfer_created_when_coop_and_plan_price_per_unit_are_equal(
        self,
    ) -> None:
        self.service.create_compensation_transfer(
            coop_price_per_unit=Decimal(3),
            plan_price_per_unit=Decimal(3),
            consumed_amount=1,
            cooperation_account=uuid4(),
            planner_product_account=uuid4(),
        )
        transfers = self.get_compensation_transfers()
        assert not transfers

    @parameterized.expand(
        [
            (Decimal(15.5), Decimal(11), 1),
            (Decimal(8), Decimal(4.2), 2),
            (Decimal(1), Decimal(0), 3),
        ]
    )
    def test_compensation_for_coop_gets_created_when_coop_price_per_unit_is_higher_than_plan_price_per_unit(
        self,
        coop_price_per_unit: Decimal,
        plan_price_per_unit: Decimal,
        consumed_amount: int,
    ) -> None:
        EXPECTED_TYPE = TransferType.compensation_for_coop
        EXPECTED_TIME = datetime(2025, 1, 1, 10, 15)
        EXPECTED_DEBIT_ACCOUNT = self.database_gateway.create_account().id
        EXPECTED_CREDIT_ACCOUNT = self.database_gateway.create_account().id
        EXPECTED_VALUE = (
            abs(coop_price_per_unit - plan_price_per_unit) * consumed_amount
        )
        self.datetime_service.freeze_time(EXPECTED_TIME)
        self.service.create_compensation_transfer(
            coop_price_per_unit=coop_price_per_unit,
            plan_price_per_unit=plan_price_per_unit,
            consumed_amount=consumed_amount,
            cooperation_account=EXPECTED_CREDIT_ACCOUNT,
            planner_product_account=EXPECTED_DEBIT_ACCOUNT,
        )
        self.datetime_service.unfreeze_time()
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].date == EXPECTED_TIME
        assert transfers[0].debit_account == EXPECTED_DEBIT_ACCOUNT
        assert transfers[0].credit_account == EXPECTED_CREDIT_ACCOUNT
        assert transfers[0].value == EXPECTED_VALUE
        assert transfers[0].type == EXPECTED_TYPE

    @parameterized.expand(
        [
            (Decimal(11), Decimal(15.5), 1),
            (Decimal(4.2), Decimal(8), 2),
            (Decimal(0), Decimal(1), 3),
        ]
    )
    def test_compensation_for_company_gets_created_when_coop_price_per_unit_is_lower_than_plan_price_per_unit(
        self,
        coop_price_per_unit: Decimal,
        plan_price_per_unit: Decimal,
        consumed_amount: int,
    ) -> None:
        EXPECTED_TYPE = TransferType.compensation_for_company
        EXPECTED_TIME = datetime(2025, 1, 1, 10, 15)
        EXPECTED_DEBIT_ACCOUNT = self.database_gateway.create_account().id
        EXPECTED_CREDIT_ACCOUNT = self.database_gateway.create_account().id
        EXPECTED_VALUE = (
            abs(coop_price_per_unit - plan_price_per_unit) * consumed_amount
        )
        self.datetime_service.freeze_time(EXPECTED_TIME)
        self.service.create_compensation_transfer(
            coop_price_per_unit=coop_price_per_unit,
            plan_price_per_unit=plan_price_per_unit,
            consumed_amount=consumed_amount,
            cooperation_account=EXPECTED_DEBIT_ACCOUNT,
            planner_product_account=EXPECTED_CREDIT_ACCOUNT,
        )
        self.datetime_service.unfreeze_time()
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].date == EXPECTED_TIME
        assert transfers[0].debit_account == EXPECTED_DEBIT_ACCOUNT
        assert transfers[0].credit_account == EXPECTED_CREDIT_ACCOUNT
        assert transfers[0].value == EXPECTED_VALUE
        assert transfers[0].type == EXPECTED_TYPE

    def get_compensation_transfers(self) -> list[Transfer]:
        transfers = self.database_gateway.get_transfers()
        return list(
            filter(
                lambda t: t.type == TransferType.compensation_for_coop
                or t.type == TransferType.compensation_for_company,
                transfers,
            )
        )
