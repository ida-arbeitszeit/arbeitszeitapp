from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit_flask.database.repositories import (
    AccountRepository,
    DatabaseGatewayImpl,
)
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    PlanGenerator,
    PurchaseGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.flask_integration.flask import FlaskTestCase


class LabourCertificatesPayoutTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.account_repository = self.injector.get(AccountRepository)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_first_payout_is_none_if_no_payouts_are_in_db(self) -> None:
        assert self.database_gateway.get_labour_certificates_payouts().first() is None

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
        sending_account = self.account_repository.create_account()
        receiving_account = self.account_repository.create_account()
        transaction = self.database_gateway.create_transaction(
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


class CompanyPurchaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_by_default_no_company_purchases_are_in_db(self) -> None:
        assert not self.database_gateway.get_company_purchases()

    def test_that_there_are_some_company_purchases_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        assert self.database_gateway.get_company_purchases()

    def test_that_retrieved_purchase_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan.id)
        purchase = self.database_gateway.get_company_purchases().first()
        assert purchase
        assert purchase.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        purchase_1 = self.database_gateway.get_company_purchases().first()
        purchase_2 = self.database_gateway.get_company_purchases().first()
        assert purchase_1
        assert purchase_2
        assert purchase_1.transaction_id == purchase_2.transaction_id

    def test_that_transaction_id_for_two_different_purchases_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        self.purchase_generator.create_resource_purchase_by_company()
        purchase_1, purchase_2 = list(self.database_gateway.get_company_purchases())
        assert purchase_1.transaction_id != purchase_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_purchase(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_resource_purchase_by_company(
            amount=expected_amount
        )
        purchase = self.database_gateway.get_company_purchases().first()
        assert purchase
        assert purchase.amount == expected_amount

    def test_can_filter_purchases_by_company(self) -> None:
        company = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        purchases = self.database_gateway.get_company_purchases()
        assert purchases.where_buyer_is_company(company)
        assert not purchases.where_buyer_is_company(other_company)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(plan=plan_2.id)
        purchase_1, purchase_2 = list(
            self.database_gateway.get_company_purchases().ordered_by_creation_date(
                ascending=True
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id
        purchase_2, purchase_1 = list(
            self.database_gateway.get_company_purchases().ordered_by_creation_date(
                ascending=False
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        result = (
            self.database_gateway.get_company_purchases()
            .with_transaction_and_plan()
            .first()
        )
        assert result
        purchase, transaction, plan = result
        assert purchase.transaction_id == transaction.id
        assert purchase.plan_id == plan.id

    def test_can_retrieve_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_resource_purchase_by_company()
        result = (
            self.database_gateway.get_company_purchases().with_transaction().first()
        )
        assert result
        purchase, transaction = result
        assert purchase.transaction_id == transaction.id

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions_and_plans(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        assert (
            self.database_gateway.get_company_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_company(company)
            .with_transaction_and_plan()
        )

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        assert (
            self.database_gateway.get_company_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_company(company)
            .with_transaction()
        )


class ConsumerPurchaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(1000)

    def test_that_by_default_no_member_purchases_are_in_db(self) -> None:
        assert not self.database_gateway.get_consumer_purchases()

    def test_that_there_are_some_member_purchases_in_db_after_one_was_created(
        self,
    ) -> None:
        self.purchase_generator.create_purchase_by_member()
        assert self.database_gateway.get_consumer_purchases()

    def test_that_retrieved_purchase_contains_specified_plan_id(self) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan.id)
        purchase = self.database_gateway.get_consumer_purchases().first()
        assert purchase
        assert purchase.plan_id == plan.id

    def test_that_transaction_id_retrieved_is_the_same_twice_in_a_row(self) -> None:
        self.purchase_generator.create_purchase_by_member()
        purchase_1 = self.database_gateway.get_consumer_purchases().first()
        purchase_2 = self.database_gateway.get_consumer_purchases().first()
        assert purchase_1
        assert purchase_2
        assert purchase_1.transaction_id == purchase_2.transaction_id

    def test_that_transaction_id_for_two_different_purchases_is_also_different(
        self,
    ) -> None:
        self.purchase_generator.create_purchase_by_member()
        self.purchase_generator.create_purchase_by_member()
        purchase_1, purchase_2 = list(self.database_gateway.get_consumer_purchases())
        assert purchase_1.transaction_id != purchase_2.transaction_id

    def test_that_amount_is_retrieved_with_the_same_value_as_specified_when_creating_the_purchase(
        self,
    ) -> None:
        expected_amount = 123
        self.purchase_generator.create_purchase_by_member(amount=expected_amount)
        purchase = self.database_gateway.get_consumer_purchases().first()
        assert purchase
        assert purchase.amount == expected_amount

    def test_can_filter_purchases_by_member(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(buyer=member)
        purchases = self.database_gateway.get_consumer_purchases()
        assert purchases.where_buyer_is_member(member)
        assert not purchases.where_buyer_is_member(other_member)

    def test_that_plans_can_be_ordered_by_creation_date(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        plan_1 = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan_1.id)
        self.datetime_service.advance_time(timedelta(days=1))
        plan_2 = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan_2.id)
        purchase_1, purchase_2 = list(
            self.database_gateway.get_consumer_purchases().ordered_by_creation_date(
                ascending=True
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id
        purchase_2, purchase_1 = list(
            self.database_gateway.get_consumer_purchases().ordered_by_creation_date(
                ascending=False
            )
        )
        assert purchase_1.plan_id == plan_1.id
        assert purchase_2.plan_id == plan_2.id

    def test_can_retrieve_plan_and_transaction_with_purchase(self) -> None:
        self.purchase_generator.create_purchase_by_member()
        result = (
            self.database_gateway.get_consumer_purchases()
            .with_transaction_and_plan()
            .first()
        )
        assert result
        purchase, transaction, plan = result
        assert purchase.transaction_id == transaction.id
        assert purchase.plan_id == plan.id

    def test_can_combine_filtering_and_joining_of_purchases_with_transactions_and_plans(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        self.purchase_generator.create_purchase_by_member(buyer=member)
        assert (
            self.database_gateway.get_consumer_purchases()
            .ordered_by_creation_date()
            .where_buyer_is_member(member)
            .with_transaction_and_plan()
        )
