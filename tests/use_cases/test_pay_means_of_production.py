from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.entities import Company, ProductionCosts, PurposesOfPurchases
from arbeitszeit.use_cases import (
    GetCompanyTransactions,
    PayMeansOfProduction,
    PayMeansOfProductionRequest,
)
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsResponse
from tests.data_generators import CooperationGenerator

from .base_test_case import BaseTestCase
from .repositories import CompanyRepository, PurchaseRepository, TransactionRepository


class PayMeansOfProductionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.pay_means_of_production = self.injector.get(PayMeansOfProduction)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.purchase_repository = self.injector.get(PurchaseRepository)
        self.transaction_repository = self.injector.get(TransactionRepository)
        self.update_plans_and_payout = self.injector.get(UpdatePlansAndPayout)
        self.company_repository = self.injector.get(CompanyRepository)

    def test_reject_payment_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(timeframe=1)
        self.update_plans_and_payout()
        self.datetime_service.freeze_time(datetime(2001, 1, 1))
        self.update_plans_and_payout()
        purpose = PurposesOfPurchases.means_of_prod
        pieces = 5
        plan.expired = True
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_is_not_active

    def test_payment_is_rejected_when_purpose_is_consumption(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        purpose = PurposesOfPurchases.consumption
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.invalid_purpose

    def test_reject_payment_trying_to_pay_public_service(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            is_public_service=True,
            activation_date=self.datetime_service.now_minus_one_day(),
        )
        purpose = PurposesOfPurchases.means_of_prod
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.cannot_buy_public_service
        )

    def test_reject_payment_trying_to_pay_own_product(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(), planner=sender
        )
        purpose = PurposesOfPurchases.means_of_prod
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.buyer_is_planner

    def test_balance_of_buyer_of_means_of_prod_reduced(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.means_of_prod
        pieces = 5

        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )

        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            self.balance_checker.get_company_account_balances(sender.id).p_account
            == -price_total
        )

    def test_balance_of_buyer_of_raw_materials_reduced(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.raw_materials
        pieces = 5

        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )

        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            self.balance_checker.get_company_account_balances(sender.id).r_account
            == -price_total
        )

    def test_balance_of_seller_increased(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            ),
            amount=5,
        )
        purpose = PurposesOfPurchases.raw_materials
        pieces = 5
        assert self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account == Decimal("-3")
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        assert self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account == Decimal("0")

    def test_balance_of_seller_increased_correctly_when_plan_is_in_cooperation(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            amount=50,
            cooperation=coop,
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            amount=200,
            cooperation=coop,
        )
        purpose = PurposesOfPurchases.raw_materials
        pieces = 5
        balance_before_transaction = self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        assert (
            self.balance_checker.get_company_account_balances(plan.planner).prd_account
            == balance_before_transaction
            + self.price_checker.get_unit_cost(plan.id) * 5
        )

    def test_correct_transaction_added_if_means_of_production_were_paid(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.means_of_prod
        pieces = 5
        transactions_before_payment = len(
            self.transaction_repository.get_transactions()
        )
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            len(self.transaction_repository.get_transactions())
            == transactions_before_payment + 1
        )
        latest_transaction = (
            self.transaction_repository.get_transactions()
            .ordered_by_transaction_date(descending=True)
            .first()
        )
        assert latest_transaction
        assert latest_transaction.sending_account == sender.means_account
        assert latest_transaction.receiving_account == self.get_product_account(
            plan.planner
        )
        assert latest_transaction.amount_sent == price_total
        assert latest_transaction.amount_received == price_total

    def test_correct_transaction_added_if_raw_materials_were_paid(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.raw_materials
        pieces = 5
        transactions_before_payment = len(
            self.transaction_repository.get_transactions()
        )
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            len(self.transaction_repository.get_transactions())
            == transactions_before_payment + 1
        )
        latest_transaction = (
            self.transaction_repository.get_transactions()
            .ordered_by_transaction_date(descending=True)
            .first()
        )
        assert latest_transaction
        assert latest_transaction.sending_account == sender.raw_material_account
        assert latest_transaction.receiving_account == self.get_product_account(
            plan.planner
        )
        assert latest_transaction.amount_sent == price_total
        assert latest_transaction.amount_received == price_total

    def test_correct_purchase_added_if_means_of_production_were_paid(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.means_of_prod
        pieces = 5
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        purchase_added = self.purchase_repository.purchases[0]
        assert len(self.purchase_repository.purchases) == 1
        assert purchase_added.plan == plan.id
        assert purchase_added.price_per_unit == self.price_checker.get_unit_price(
            plan.id
        )
        assert purchase_added.amount == pieces
        assert purchase_added.purpose == PurposesOfPurchases.means_of_prod
        assert purchase_added.buyer == sender.id
        assert purchase_added.plan == plan.id
        assert purchase_added.is_buyer_a_member == False

    def test_correct_purchase_added_if_raw_materials_were_paid(self) -> None:
        sender = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        purpose = PurposesOfPurchases.raw_materials
        pieces = 5
        self.pay_means_of_production(
            PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
        )
        purchase_added = self.purchase_repository.purchases[0]
        assert len(self.purchase_repository.purchases) == 1
        assert purchase_added.plan == plan.id
        assert purchase_added.price_per_unit == self.price_checker.get_unit_price(
            plan.id
        )
        assert purchase_added.amount == pieces
        assert purchase_added.purpose == PurposesOfPurchases.raw_materials
        assert purchase_added.buyer == sender.id
        assert purchase_added.plan == plan.id
        assert purchase_added.is_buyer_a_member == False

    def test_plan_not_found_rejects_payment(self) -> None:
        buyer = self.company_generator.create_company_entity()
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(
                buyer=buyer.id,
                plan=uuid4(),
                amount=1,
                purpose=PurposesOfPurchases.means_of_prod,
            )
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_plan_found_accepts_payment(self) -> None:
        buyer = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(activation_date=datetime.min)
        response = self.pay_means_of_production(
            PayMeansOfProductionRequest(
                buyer=buyer.id,
                plan=plan.id,
                amount=1,
                purpose=PurposesOfPurchases.means_of_prod,
            )
        )
        assert not response.is_rejected
        assert response.rejection_reason is None

    def get_product_account(self, company: UUID) -> UUID:
        company_model = self.company_repository.get_companies().with_id(company).first()
        assert company_model
        return company_model.product_account


class TestSuccessfulPayment(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.buyer = self.company_generator.create_company_entity()
        self.planner = self.company_generator.create_company_entity()
        self.plan = self.plan_generator.create_plan(
            planner=self.planner, activation_date=datetime.min
        )
        self.pay_means_of_production = self.injector.get(PayMeansOfProduction)
        self.get_company_transactions = self.injector.get(GetCompanyTransactions)
        self.transaction_time = datetime(2020, 10, 1, 22, 30)
        self.datetime_service.freeze_time(self.transaction_time)
        self.planner_transactions_before_payment = len(
            self.get_company_transactions(self.planner.id).transactions
        )
        self.response = self.pay_means_of_production(
            PayMeansOfProductionRequest(
                buyer=self.buyer.id,
                plan=self.plan.id,
                amount=1,
                purpose=PurposesOfPurchases.means_of_prod,
            )
        )
        self.datetime_service.freeze_time(self.transaction_time + timedelta(days=1))

    def test_transaction_shows_up_in_transaction_listing_for_buyer(self) -> None:
        transaction_info = self.get_buyer_transaction_infos(self.buyer)
        self.assertEqual(len(transaction_info.transactions), 1)

    def test_transaction_shows_up_in_transaction_listing_for_planner(self) -> None:
        transaction_info = self.get_company_transactions(self.planner.id)
        self.assertEqual(
            len(transaction_info.transactions),
            self.planner_transactions_before_payment + 1,
        )

    def test_transaction_info_of_buyer_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_company_transactions(self.buyer.id)
        self.assertEqual(transaction_info.transactions[0].date, self.transaction_time)

    def test_transaction_info_of_planner_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_company_transactions(self.planner.id)
        self.assertEqual(transaction_info.transactions[-1].date, self.transaction_time)

    def get_buyer_transaction_infos(
        self, user: Company
    ) -> GetCompanyTransactionsResponse:
        return self.get_company_transactions(user.id)
