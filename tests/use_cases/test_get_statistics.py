from decimal import Decimal
from typing import Union
from unittest import TestCase

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import GetStatistics
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout
from tests.data_generators import (
    CompanyGenerator,
    CooperationGenerator,
    MemberGenerator,
    PlanGenerator,
    TransactionGenerator,
)
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector

Number = Union[int, Decimal]


def production_costs(p: Number, r: Number, a: Number) -> ProductionCosts:
    return ProductionCosts(
        Decimal(p),
        Decimal(r),
        Decimal(a),
    )


class GetStatisticsTester(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(GetStatistics)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.update_plans_and_payout = self.injector.get(UpdatePlansAndPayout)
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_values_are_zero_if_repositories_are_empty(self) -> None:
        stats = self.use_case()
        assert stats.registered_companies_count == 0
        assert stats.registered_members_count == 0
        assert stats.active_plans_count == 0
        assert stats.active_plans_public_count == 0
        assert stats.avg_timeframe == 0
        assert stats.planned_work == 0
        assert stats.planned_resources == 0
        assert stats.planned_means == 0

    def test_counting_of_companies(self) -> None:
        self.company_generator.create_company_entity()
        self.company_generator.create_company_entity()
        stats = self.use_case()
        assert stats.registered_companies_count == 2

    def test_counting_of_members(self) -> None:
        self.member_generator.create_member_entity()
        self.member_generator.create_member_entity()
        stats = self.use_case()
        assert stats.registered_members_count == 2

    def test_counting_of_cooperations(self) -> None:
        number_of_coops = 2
        for _ in range(number_of_coops):
            self.cooperation_generator.create_cooperation()
        stats = self.use_case()
        assert stats.cooperations_count == number_of_coops

    def test_counting_of_certificates_when_certs_are_zero(self) -> None:
        stats = self.use_case()
        assert stats.certificates_count == 0

    def test_counting_of_certificates_when_two_members_have_received_certs(
        self,
    ) -> None:
        num_transactions = 2
        for _ in range(num_transactions):
            worker = self.member_generator.create_member_entity()
            account = worker.account
            self.transaction_generator.create_transaction(
                receiving_account=account,
                amount_received=Decimal(10),
            )
        stats = self.use_case()
        assert stats.certificates_count == num_transactions * Decimal(10)

    def test_counting_of_certificates_when_one_worker_and_one_company_have_received_certs(
        self,
    ) -> None:
        # worker receives certs
        worker = self.member_generator.create_member_entity()
        worker_account = worker.account
        self.transaction_generator.create_transaction(
            receiving_account=worker_account,
            amount_received=Decimal(10.5),
        )
        # company receives certs
        company = self.company_generator.create_company_entity()
        company_account = company.work_account
        self.transaction_generator.create_transaction(
            receiving_account=company_account, amount_received=Decimal(10)
        )
        stats = self.use_case()
        assert stats.certificates_count == Decimal(20.5)

    def test_available_product_is_positive_number_when_amount_on_prd_account_is_negative(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account, amount_received=Decimal(-10)
        )
        stats = self.use_case()
        assert stats.available_product == Decimal(10)

    def test_correct_available_product_is_shown_when_two_companies_have_received_prd_debit(
        self,
    ) -> None:
        num_companies = 2
        for _ in range(num_companies):
            company = self.company_generator.create_company_entity()
            self.transaction_generator.create_transaction(
                receiving_account=company.product_account, amount_received=Decimal(-22)
            )
        stats = self.use_case()
        assert stats.available_product == num_companies * Decimal(22)

    def test_counting_of_active_plans(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day()
        )
        stats = self.use_case()
        assert stats.active_plans_count == 2

    def test_counting_of_plans_that_are_both_active_and_public(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            is_public_service=True,
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            is_public_service=True,
        )
        stats = self.use_case()
        assert stats.active_plans_public_count == 2

    def test_that_inactive_and_productive_plans_are_ignored_when_counting_active_and_public_plans(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            is_public_service=False,
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            is_public_service=True,
        )
        stats = self.use_case()
        assert stats.active_plans_public_count == 1

    def test_average_calculation_of_two_active_plan_timeframes(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(), timeframe=3
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(), timeframe=7
        )
        stats = self.use_case()
        assert stats.avg_timeframe == 5

    def test_adding_up_work_of_two_plans(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(3, 1, 1),
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(2, 1, 1),
        )
        stats = self.use_case()
        assert stats.planned_work == 5

    def test_adding_up_resources_of_two_plans(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(1, 3, 1),
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(1, 2, 1),
        )
        stats = self.use_case()
        assert stats.planned_resources == 5

    def test_adding_up_means_of_two_plans(self) -> None:
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(1, 1, 3),
        )
        self.plan_generator.create_plan(
            activation_date=self.datetime_service.now_minus_one_day(),
            costs=production_costs(1, 1, 2),
        )
        stats = self.use_case()
        assert stats.planned_means == 5

    def test_that_use_case_returns_none_for_payout_factor_if_it_never_has_been_calculated(
        self,
    ) -> None:
        stats = self.use_case()
        assert stats.payout_factor is None

    def test_that_use_case_shows_payout_factor_if_it_has_been_calculated(self) -> None:
        self.update_plans_and_payout()
        stats = self.use_case()
        assert stats.payout_factor is not None
