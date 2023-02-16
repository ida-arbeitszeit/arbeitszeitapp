from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit import entities
from arbeitszeit_flask.database.repositories import (
    AccountRepository,
    DatabaseGatewayImpl,
    TransactionRepository,
)
from tests.data_generators import PlanGenerator

from .flask import FlaskTestCase


class LabourCertificatesPayoutTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.transaction_repository = self.injector.get(TransactionRepository)
        self.account_repository = self.injector.get(AccountRepository)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_by_default_no_payouts_are_found_in_db(self) -> None:
        assert not self.database_gateway.get_labour_certificates_payouts()

    def test_that_some_payouts_are_found_if_one_was_created_previously(self) -> None:
        plan = self.plan_generator.create_plan()
        self.database_gateway.create_labour_certificates_payout(
            transaction=self.create_transaction(),
            plan=plan.id,
        )
        assert self.database_gateway.get_labour_certificates_payouts()

    def test_that_3_payouts_were_registered_if_3_were_created(self) -> None:
        plan = self.plan_generator.create_plan()
        for _ in range(3):
            self.database_gateway.create_labour_certificates_payout(
                transaction=self.create_transaction(),
                plan=plan.id,
            )
        assert len(self.database_gateway.get_labour_certificates_payouts()) == 3

    def test_that_retrieved_payout_containts_plan_id_that_it_was_created_with(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.database_gateway.create_labour_certificates_payout(
            transaction=self.create_transaction(),
            plan=plan.id,
        )
        for payout in self.database_gateway.get_labour_certificates_payouts():
            assert payout.plan_id == plan.id

    def test_that_retrieved_payout_contains_the_transaction_id_that_it_was_created_with(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        transaction = self.create_transaction()
        self.database_gateway.create_labour_certificates_payout(
            transaction=transaction,
            plan=plan.id,
        )
        for payout in self.database_gateway.get_labour_certificates_payouts():
            assert payout.transaction_id == transaction

    def test_that_returned_payout_contains_plan_id_that_it_was_created_with(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        transaction = self.create_transaction()
        payout = self.database_gateway.create_labour_certificates_payout(
            transaction=transaction,
            plan=plan.id,
        )
        assert payout.plan_id == plan.id

    def test_that_no_payouts_are_returned_when_filtering_for_non_existing_plan(
        self,
    ) -> None:
        self.database_gateway.create_labour_certificates_payout(
            transaction=self.create_transaction(),
            plan=self.plan_generator.create_plan().id,
        )
        assert not self.database_gateway.get_labour_certificates_payouts().for_plan(
            uuid4()
        )

    def test_that_a_payout_is_returned_when_filtering_for_existing_plan(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan().id
        self.database_gateway.create_labour_certificates_payout(
            transaction=self.create_transaction(),
            plan=plan,
        )
        assert self.database_gateway.get_labour_certificates_payouts().for_plan(plan)

    def create_transaction(self) -> UUID:
        sending_account = self.account_repository.create_account(
            entities.AccountTypes.accounting
        )
        receiving_account = self.account_repository.create_account(
            entities.AccountTypes.a
        )
        transaction = self.transaction_repository.create_transaction(
            date=datetime(2000, 1, 1),
            sending_account=sending_account.id,
            receiving_account=receiving_account.id,
            purpose="",
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
        )
        return transaction.id


class PayoutFactorTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)

    def test_that_returned_payout_factor_is_equal_to_specified_value_on_creation(
        self,
    ) -> None:
        expected_values = [Decimal("0.5"), Decimal("0")]
        for expected_value in expected_values:
            factor = self.database_gateway.create_payout_factor(
                timestamp=datetime(2000, 1, 1), payout_factor=expected_value
            )
            assert factor.value == expected_value

    def test_that_returned_calulcation_date_is_equal_to_specified_timestamp_on_creation(
        self,
    ) -> None:
        expected_timestamps = [datetime(2000, 2, 2), datetime(2050, 1, 1)]
        for expected_timestamp in expected_timestamps:
            factor = self.database_gateway.create_payout_factor(
                timestamp=expected_timestamp, payout_factor=Decimal(0)
            )
            assert factor.calculation_date == expected_timestamp

    def test_a_priori_no_payout_factor_is_stored_in_db(self) -> None:
        assert not self.database_gateway.get_payout_factors()

    def test_that_some_payout_factors_are_queried_after_one_payout_factor_was_created(
        self,
    ) -> None:
        self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 1),
            payout_factor=Decimal(1),
        )
        assert self.database_gateway.get_payout_factors()

    def test_that_created_payout_factor_is_in_queried_results(
        self,
    ) -> None:
        factor_1 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 1),
            payout_factor=Decimal(1),
        )
        factor_2 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 1),
            payout_factor=Decimal(0),
        )
        factor_3 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 2),
            payout_factor=Decimal(0),
        )
        assert factor_1 in self.database_gateway.get_payout_factors()
        assert factor_2 in self.database_gateway.get_payout_factors()
        assert factor_3 in self.database_gateway.get_payout_factors()

    def test_that_payout_factors_can_be_ordered_by_calculation_date_ascending(
        self,
    ) -> None:
        factor_1 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 1),
            payout_factor=Decimal(1),
        )
        factor_2 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 2),
            payout_factor=Decimal(1),
        )
        assert list(
            self.database_gateway.get_payout_factors().ordered_by_calculation_date()
        ) == [factor_1, factor_2]

    def test_that_payout_factors_can_be_ordered_by_calculation_date_descending(
        self,
    ) -> None:
        factor_1 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 1),
            payout_factor=Decimal(1),
        )
        factor_2 = self.database_gateway.create_payout_factor(
            timestamp=datetime(2000, 1, 2),
            payout_factor=Decimal(1),
        )
        assert list(
            self.database_gateway.get_payout_factors().ordered_by_calculation_date(
                descending=True
            )
        ) == [factor_2, factor_1]
