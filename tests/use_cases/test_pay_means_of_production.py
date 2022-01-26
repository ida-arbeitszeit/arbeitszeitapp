from datetime import datetime, timedelta
from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import Company, PurposesOfPurchases
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.use_cases import (
    GetTransactionInfos,
    PayMeansOfProduction,
    PayMeansOfProductionRequest,
    TransactionInfo,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector, injection_test
from .repositories import (
    AccountRepository,
    PlanCooperationRepository,
    PurchaseRepository,
    TransactionRepository,
)


@injection_test
def test_error_is_raised_if_plan_is_not_active_yet(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan()
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    response = pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_is_not_active


@injection_test
def test_reject_payment_if_plan_is_expired(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        plan_creation_date=datetime_service.now_minus_ten_days(), timeframe=1
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    plan.expired = True
    response = pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_is_not_active


@injection_test
def test_payment_is_rejected_when_purpose_is_consumption(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.min)
    purpose = PurposesOfPurchases.consumption
    response = pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.invalid_purpose


@injection_test
def test_reject_payment_trying_to_pay_public_service(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        is_public_service=True, activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    response = pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
    )
    assert response.is_rejected
    assert (
        response.rejection_reason == response.RejectionReason.cannot_buy_public_service
    )


@injection_test
def test_reject_payment_trying_to_pay_own_product(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), planner=sender
    )
    purpose = PurposesOfPurchases.means_of_prod
    response = pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, 5, purpose)
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.buyer_is_planner


@injection_test
def test_balance_of_buyer_of_means_of_prod_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    price_total = pieces * calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert account_repository.get_account_balance(sender.means_account) == -price_total


@injection_test
def test_balance_of_buyer_of_raw_materials_reduced(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    price_total = pieces * calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert (
        account_repository.get_account_balance(sender.raw_material_account)
        == -price_total
    )


@injection_test
def test_balance_of_seller_increased(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    # account prd shows the originally planned cost of the sold product
    # (the coop price is irrelevant here)
    planed_cost_of_product = pieces * calculate_price([plan])
    assert (
        account_repository.get_account_balance(plan.planner.product_account)
        == planed_cost_of_product
    )


@injection_test
def test_balance_of_seller_increased_correctly_when_plan_is_in_cooperation(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
    cooperation_generator: CooperationGenerator,
):
    coop = cooperation_generator.create_cooperation()
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        amount=50,
        cooperation=coop,
    )
    plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        amount=200,
        cooperation=coop,
    )

    purpose = PurposesOfPurchases.raw_materials
    pieces = 5

    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )

    planed_cost_of_product = pieces * calculate_price([plan])
    assert (
        account_repository.get_account_balance(plan.planner.product_account)
        == planed_cost_of_product
    )


@injection_test
def test_correct_transaction_added_if_means_of_production_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    price_total = pieces * calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert len(transaction_repository.transactions) == 1
    assert (
        transaction_repository.transactions[0].sending_account == sender.means_account
    )
    assert (
        transaction_repository.transactions[0].receiving_account
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount_sent == price_total
    assert transaction_repository.transactions[0].amount_received == price_total


@injection_test
def test_correct_transaction_added_if_raw_materials_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    price_total = pieces * calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert len(transaction_repository.transactions) == 1
    assert (
        transaction_repository.transactions[0].sending_account
        == sender.raw_material_account
    )
    assert (
        transaction_repository.transactions[0].receiving_account
        == plan.planner.product_account
    )
    assert transaction_repository.transactions[0].amount_sent == price_total
    assert transaction_repository.transactions[0].amount_received == price_total


@injection_test
def test_correct_purchase_added_if_means_of_production_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.means_of_prod
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    purchase_added = purchase_repository.purchases[0]
    assert len(purchase_repository.purchases) == 1
    assert purchase_added.plan == plan
    assert purchase_added.price_per_unit == calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert purchase_added.amount == pieces
    assert purchase_added.purpose == PurposesOfPurchases.means_of_prod
    assert purchase_added.buyer == sender
    assert purchase_added.plan == plan


@injection_test
def test_correct_purchase_added_if_raw_materials_were_paid(
    pay_means_of_production: PayMeansOfProduction,
    purchase_repository: PurchaseRepository,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    plan_cooperation_repository: PlanCooperationRepository,
):
    sender = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day()
    )
    purpose = PurposesOfPurchases.raw_materials
    pieces = 5
    pay_means_of_production(
        PayMeansOfProductionRequest(sender.id, plan.id, pieces, purpose)
    )
    purchase_added = purchase_repository.purchases[0]
    assert len(purchase_repository.purchases) == 1
    assert purchase_added.plan == plan
    assert purchase_added.price_per_unit == calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan.id)
    )
    assert purchase_added.amount == pieces
    assert purchase_added.purpose == PurposesOfPurchases.raw_materials
    assert purchase_added.buyer == sender
    assert purchase_added.plan == plan


@injection_test
def test_plan_not_found_rejects_payment(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
) -> None:
    buyer = company_generator.create_company()
    response = pay_means_of_production(
        PayMeansOfProductionRequest(
            buyer=buyer.id,
            plan=uuid4(),
            amount=1,
            purpose=PurposesOfPurchases.means_of_prod,
        )
    )
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_not_found


@injection_test
def test_plan_found_accepts_payment(
    pay_means_of_production: PayMeansOfProduction,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
) -> None:
    buyer = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.min)
    response = pay_means_of_production(
        PayMeansOfProductionRequest(
            buyer=buyer.id,
            plan=plan.id,
            amount=1,
            purpose=PurposesOfPurchases.means_of_prod,
        )
    )
    assert not response.is_rejected
    assert response.rejection_reason is None


class TestSuccessfulPayment(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.buyer = self.company_generator.create_company()
        self.planner = self.company_generator.create_company()
        self.plan = self.plan_generator.create_plan(
            planner=self.planner, activation_date=datetime.min
        )
        self.pay_means_of_production = self.injector.get(PayMeansOfProduction)
        self.get_transaction_infos = self.injector.get(GetTransactionInfos)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.transaction_time = datetime(2020, 10, 1, 22, 30)
        self.datetime_service.freeze_time(self.transaction_time)
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
        self.assertEqual(len(transaction_info), 1)

    def test_transaction_shows_up_in_transaction_listing_for_planner(self) -> None:
        transaction_info = self.get_transaction_infos(self.planner)
        self.assertEqual(len(transaction_info), 1)

    def test_transaction_info_of_buyer_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_transaction_infos(self.buyer)
        self.assertEqual(transaction_info[0].date, self.transaction_time)

    def test_transaction_info_of_planner_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_transaction_infos(self.planner)
        self.assertEqual(transaction_info[0].date, self.transaction_time)

    def get_buyer_transaction_infos(self, user: Company) -> List[TransactionInfo]:
        return self.get_transaction_infos(user)
