from datetime import timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionInteractor,
    RegisterProductiveConsumptionRequest,
)
from arbeitszeit.records import (
    ConsumptionType,
    ProductionCosts,
    ProductiveConsumption,
    Transfer,
)
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc

from .base_test_case import BaseTestCase


class InteractorBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(RegisterProductiveConsumptionInteractor)

    def _get_transfers_of_type(self, transfer_type: TransferType) -> list[Transfer]:
        return list(
            filter(
                lambda t: t.type == transfer_type,
                self.database_gateway.get_transfers(),
            )
        )


class TestRejection(InteractorBase):
    def test_reject_registration_if_plan_not_found(self) -> None:
        consumer = self.company_generator.create_company()
        response = self.interactor.execute(
            RegisterProductiveConsumptionRequest(
                consumer=consumer,
                plan=uuid4(),
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_reject_registration_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.freeze_time(datetime_utc(2001, 1, 1))
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5
        response = self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, pieces, consumption_type)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_is_not_active

    def test_registration_is_rejected_when_consumption_type_is_private_consumption(
        self,
    ) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.consumption
        response = self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, 5, consumption_type)
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.invalid_consumption_type
        )

    def test_reject_registration_trying_to_consume_public_service(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(is_public_service=True)
        consumption_type = ConsumptionType.means_of_prod
        response = self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, 5, consumption_type)
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.cannot_consume_public_service
        )

    def test_reject_registration_trying_to_consume_own_product(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=sender)
        consumption_type = ConsumptionType.means_of_prod
        response = self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, 5, consumption_type)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.consumer_is_planner


class TestBalanceChanges(InteractorBase):
    def test_balance_of_consumer_gets_reduced(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5

        self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, pieces, consumption_type)
        )

        price_total = pieces * self.price_checker.get_price_per_unit(plan)
        assert (
            self.balance_checker.get_company_account_balances(sender).p_account
            == -price_total
        )

    def test_balance_of_consumer_of_raw_materials_reduced(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.raw_materials
        pieces = 5

        self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, pieces, consumption_type)
        )

        price_total = pieces * self.price_checker.get_price_per_unit(plan)
        assert (
            self.balance_checker.get_company_account_balances(sender).r_account
            == -price_total
        )

    def test_balance_of_seller_increased(self) -> None:
        sender = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            ),
            amount=5,
            planner=planner,
        )
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        assert self.balance_checker.get_company_account_balances(
            planner
        ).prd_account == Decimal("-3")
        self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, pieces, consumption_type)
        )
        assert self.balance_checker.get_company_account_balances(
            planner
        ).prd_account == Decimal("0")

    def test_balance_of_seller_increased_correctly_when_plan_is_in_cooperation(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        sender = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            amount=50, cooperation=coop, planner=planner
        )
        self.plan_generator.create_plan(amount=200, cooperation=coop)
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        balance_before_transfer = self.balance_checker.get_company_account_balances(
            planner
        ).prd_account
        self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, pieces, consumption_type)
        )
        assert (
            self.balance_checker.get_company_account_balances(planner).prd_account
            == balance_before_transfer + self.price_checker.get_cost_per_unit(plan) * 5
        )

    def test_that_unit_cost_for_cooperating_plans_only_considers_non_expired_plans(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2010, 1, 1))
        coop = self.cooperation_generator.create_cooperation()
        sender = self.company_generator.create_company()
        self.plan_generator.create_plan(
            cooperation=coop,
            timeframe=1,
            amount=1,
            costs=ProductionCosts(
                labour_cost=Decimal(10), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        plan = self.plan_generator.create_plan(
            amount=1,
            cooperation=coop,
            timeframe=10,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        self.datetime_service.advance_time(timedelta(days=2))
        consumption_type = ConsumptionType.raw_materials
        balance_before_transfer = self.balance_checker.get_company_account_balances(
            sender
        ).r_account
        self.interactor.execute(
            RegisterProductiveConsumptionRequest(sender, plan, 1, consumption_type)
        )
        assert self.balance_checker.get_company_account_balances(
            sender
        ).r_account == balance_before_transfer - Decimal(1)


class TestConsumptionTransfers(InteractorBase):
    def test_correct_transfer_of_means_of_production_consumption_created(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        amount = 5
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer,
            plan=plan,
            amount=amount,
        )
        expected_value = amount * self.price_checker.get_price_per_unit(plan)
        transfers_of_consumption_p = self._get_transfers_of_type(
            TransferType.productive_consumption_p
        )
        assert len(transfers_of_consumption_p) == 1
        assert transfers_of_consumption_p[
            0
        ].debit_account == self.get_means_of_production_account(consumer)
        assert transfers_of_consumption_p[0].credit_account == self.get_product_account(
            planner
        )
        assert transfers_of_consumption_p[0].value == expected_value
        assert (
            transfers_of_consumption_p[0].type == TransferType.productive_consumption_p
        )

    def test_correct_value_of_means_of_production_consumption_created_if_plan_is_cooperating(
        self,
    ) -> None:
        AMOUNT = 5
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            )
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(4),
                means_cost=Decimal(4),
                resource_cost=Decimal(4),
            )
        )
        self.cooperation_generator.create_cooperation(plans=[plan_1, plan_2])
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan_1,
            amount=AMOUNT,
        )
        expected_value = AMOUNT * self.price_checker.get_price_per_unit(plan_1)
        transfers_of_consumption_p = self._get_transfers_of_type(
            TransferType.productive_consumption_p
        )
        assert len(transfers_of_consumption_p) == 1
        assert transfers_of_consumption_p[0].value == expected_value

    def test_correct_transfer_of_raw_materials_consumption_created(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        amount = 5
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer,
            plan=plan,
            amount=amount,
        )
        expected_value = amount * self.price_checker.get_price_per_unit(plan)
        transfers_of_consumption_r = self._get_transfers_of_type(
            TransferType.productive_consumption_r
        )
        assert len(transfers_of_consumption_r) == 1
        assert transfers_of_consumption_r[
            0
        ].debit_account == self.get_raw_material_account(consumer)
        assert transfers_of_consumption_r[0].credit_account == self.get_product_account(
            planner
        )
        assert transfers_of_consumption_r[0].value == expected_value
        assert (
            transfers_of_consumption_r[0].type == TransferType.productive_consumption_r
        )

    def test_correct_value_of_raw_materials_consumption_created_if_plan_is_cooperating(
        self,
    ) -> None:
        AMOUNT = 5
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            )
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(4),
                means_cost=Decimal(4),
                resource_cost=Decimal(4),
            )
        )
        self.cooperation_generator.create_cooperation(plans=[plan_1, plan_2])
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan_1, amount=AMOUNT
        )
        expected_value = self.price_checker.get_price_per_unit(plan_1) * AMOUNT
        transfers_of_consumption_r = self._get_transfers_of_type(
            TransferType.productive_consumption_r
        )
        assert len(transfers_of_consumption_r) == 1
        assert transfers_of_consumption_r[0].value == expected_value

    def get_product_account(self, company: UUID) -> UUID:
        company_model = self.database_gateway.get_companies().with_id(company).first()
        assert company_model
        return company_model.product_account

    def get_raw_material_account(self, company: UUID) -> UUID:
        company_model = self.database_gateway.get_companies().with_id(company).first()
        assert company_model
        return company_model.raw_material_account

    def get_means_of_production_account(self, company: UUID) -> UUID:
        company_model = self.database_gateway.get_companies().with_id(company).first()
        assert company_model
        return company_model.means_account


class TestCompensationTransfers(InteractorBase):
    def test_no_compensation_transfer_created_when_consumed_plan_is_not_cooperating(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        transfers = self.get_compensation_transfers()
        assert not transfers

    def test_no_compensation_transfer_created_after_consumption_of_cooperative_product_without_productivity_differences(
        self,
    ) -> None:
        COSTS_PER_UNIT = Decimal(3)
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[COSTS_PER_UNIT, COSTS_PER_UNIT]
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=cooperating_plans[0],
        )
        transfers = self.get_compensation_transfers()
        assert not transfers

    def test_no_compensation_transfer_created_when_consumed_plan_has_average_productivity(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(5), Decimal(10), Decimal(15)]
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=cooperating_plans[1],  # second plan has average productivity
        )
        transfers = self.get_compensation_transfers()
        assert not transfers

    @parameterized.expand(
        [
            (0,),
            (1,),
            (3,),
        ]
    )
    def test_one_compensation_transfer_created_for_each_consumption_of_cooperative_product_with_productivity_differences(
        self,
        number_of_consumptions: int,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_fixed_means_consumption(
                plan=cooperating_plans[0],
            )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == number_of_consumptions

    def test_that_compensation_for_cooperation_transfer_created_if_overproductive_plan_is_consumed(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=cooperating_plans[0],  # first plan is overproductive
        )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].type == TransferType.compensation_for_coop

    def test_that_compensation_for_company_created_if_underproductive_plan_is_consumed(
        self,
    ) -> None:
        cooperating_plans = self.create_cooperating_plans_with(
            costs_per_unit=[Decimal(3), Decimal(10)]
        )
        self.consumption_generator.create_fixed_means_consumption(
            plan=cooperating_plans[1],  # second plan is underproductive
        )
        transfers = self.get_compensation_transfers()
        assert len(transfers) == 1
        assert transfers[0].type == TransferType.compensation_for_company

    def create_cooperating_plans_with(
        self, *, costs_per_unit: list[Decimal]
    ) -> list[UUID]:
        plans = [self.create_plan_with(cost_per_unit=cost) for cost in costs_per_unit]
        self.cooperation_generator.create_cooperation(
            plans=plans,
        )
        return plans

    def create_plan_with(self, *, cost_per_unit: Decimal) -> UUID:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=cost_per_unit,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        return plan

    def get_compensation_transfers(self) -> list[Transfer]:
        transfers = self.database_gateway.get_transfers()
        return list(
            filter(
                lambda t: t.type == TransferType.compensation_for_coop
                or t.type == TransferType.compensation_for_company,
                transfers,
            )
        )


class TestConsumptionRecords(InteractorBase):
    @parameterized.expand(
        [
            (0),
            (1),
            (3),
        ]
    )
    def test_that_one_consumption_record_is_created_for_each_consumption_of_fixed_means(
        self, number_of_consumptions: int
    ) -> None:
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_fixed_means_consumption()
        assert len(self.get_consumption_records()) == number_of_consumptions

    @parameterized.expand(
        [
            (0),
            (1),
            (3),
        ]
    )
    def test_that_one_consumption_record_is_created_for_each_consumption_of_resource_consumption(
        self, number_of_consumptions: int
    ) -> None:
        for _ in range(number_of_consumptions):
            self.consumption_generator.create_resource_consumption_by_company()
        assert len(self.get_consumption_records()) == number_of_consumptions

    def test_that_consumption_record_for_fixed_means_has_correct_amount_and_plan_id(
        self,
    ) -> None:
        EXPECTED_PLAN = self.plan_generator.create_plan()
        EXPECTED_AMOUNT = 5
        self.consumption_generator.create_fixed_means_consumption(
            plan=EXPECTED_PLAN,
            amount=EXPECTED_AMOUNT,
        )
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].plan_id == EXPECTED_PLAN
        assert consumptions[0].amount == EXPECTED_AMOUNT

    def test_that_consumption_record_for_raw_materials_has_correct_amount_and_plan_id(
        self,
    ) -> None:
        EXPECTED_PLAN = self.plan_generator.create_plan()
        EXPECTED_AMOUNT = 5
        self.consumption_generator.create_resource_consumption_by_company(
            plan=EXPECTED_PLAN,
            amount=EXPECTED_AMOUNT,
        )
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].plan_id == EXPECTED_PLAN
        assert consumptions[0].amount == EXPECTED_AMOUNT

    def test_that_consumption_record_for_fixed_means_has_correct_transfer_of_consumption(
        self,
    ) -> None:
        self.consumption_generator.create_fixed_means_consumption()
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        consumption_transfers = self._get_transfers_of_type(
            TransferType.productive_consumption_p
        )
        assert len(consumption_transfers) == 1
        assert (
            consumptions[0].transfer_of_productive_consumption
            == consumption_transfers[0].id
        )

    def test_that_consumption_record_for_raw_materials_has_correct_transfer_of_consumption(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        consumption_transfers = self._get_transfers_of_type(
            TransferType.productive_consumption_r
        )
        assert len(consumption_transfers) == 1
        assert (
            consumptions[0].transfer_of_productive_consumption
            == consumption_transfers[0].id
        )

    def test_that_consumption_record_for_fixed_means_has_no_transfer_of_compensation_if_plan_is_not_cooperating(
        self,
    ) -> None:
        self.consumption_generator.create_fixed_means_consumption()
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].transfer_of_compensation is None

    def test_that_consumption_record_for_raw_materials_has_no_transfer_of_compensation_if_plan_is_not_cooperating(
        self,
    ) -> None:
        self.consumption_generator.create_resource_consumption_by_company()
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].transfer_of_compensation is None

    def test_that_consumption_record_for_fixed_means_has_correct_transfer_of_compensation_if_plan_is_cooperating_and_underproductive(
        self,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            )
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(4),
                means_cost=Decimal(4),
                resource_cost=Decimal(4),
            )
        )
        self.cooperation_generator.create_cooperation(plans=[plan_1, plan_2])
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan_2,  # plan_2 is underproductive
        )
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].transfer_of_compensation is not None
        compensation_transfers = self._get_transfers_of_type(
            TransferType.compensation_for_company
        )
        assert len(compensation_transfers) == 1
        assert consumptions[0].transfer_of_compensation == compensation_transfers[0].id

    def test_that_consumption_record_for_raw_materials_has_correct_transfer_of_compensation_if_plan_is_cooperating_and_underproductive(
        self,
    ) -> None:
        plan_1 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            )
        )
        plan_2 = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(4),
                means_cost=Decimal(4),
                resource_cost=Decimal(4),
            )
        )
        self.cooperation_generator.create_cooperation(plans=[plan_1, plan_2])
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan_2,  # plan_2 is underproductive
        )
        consumptions = self.get_consumption_records()
        assert len(consumptions) == 1
        assert consumptions[0].transfer_of_compensation is not None
        compensation_transfers = self._get_transfers_of_type(
            TransferType.compensation_for_company
        )
        assert len(compensation_transfers) == 1
        assert consumptions[0].transfer_of_compensation == compensation_transfers[0].id

    def get_consumption_records(self) -> list[ProductiveConsumption]:
        return list(self.database_gateway.get_productive_consumptions())
