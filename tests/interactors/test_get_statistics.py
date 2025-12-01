from datetime import timedelta
from decimal import Decimal
from typing import Union
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.decimal import decimal_sum
from arbeitszeit.interactors.get_statistics import GetStatisticsInteractor
from arbeitszeit.records import ProductionCosts
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.payout_factor import PayoutFactorService
from tests.interactors.base_test_case import BaseTestCase

Number = Union[int, Decimal]


def production_costs(p: Number, r: Number, a: Number) -> ProductionCosts:
    return ProductionCosts(
        labour_cost=Decimal(a),
        means_cost=Decimal(p),
        resource_cost=Decimal(r),
    )


class StatisticsBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetStatisticsInteractor)


class CountCompaniesTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_companies_are_counted(
        self,
        num_companies: int,
    ) -> None:
        for _ in range(num_companies):
            self.company_generator.create_company()
        stats = self.interactor.get_statistics()
        assert stats.registered_companies_count == num_companies


class CountMembersTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_number_of_members_is_counted(
        self,
        num_members: int,
    ) -> None:
        for _ in range(num_members):
            self.member_generator.create_member()
        stats = self.interactor.get_statistics()
        assert stats.registered_members_count == num_members


class CountCooperationsTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_number_of_cooperations_is_counted(
        self,
        num_cooperations: int,
    ) -> None:
        for _ in range(num_cooperations):
            self.cooperation_generator.create_cooperation()
        stats = self.interactor.get_statistics()
        assert stats.cooperations_count == num_cooperations


class CountCertificatesTests(StatisticsBaseTestCase):
    """
    Estimated total number of certificates available in the system is
    expected to be the sum of all certificates in member accounts and
    the certificates in company labour accounts multiplied by the
    current payout factor (fic).
    """

    def setUp(self) -> None:
        super().setUp()
        self.fic_service = self.injector.get(PayoutFactorService)

    def test_per_default_zero_certificates_are_counted(self) -> None:
        stats = self.interactor.get_statistics()
        assert stats.certificates_count == 0

    @parameterized.expand(
        [
            (
                Decimal(5.2),
                Decimal(3.1),
            ),
            (
                Decimal(7),
                Decimal(11),
            ),
            (
                Decimal(0),
                Decimal(0),
            ),
            (
                Decimal(0),
                Decimal(5.2),
            ),
            (
                Decimal(5.2),
                Decimal(0),
            ),
        ]
    )
    def test_that_available_certificates_are_zero_when_two_workers_or_less_have_worked_in_different_companies(
        self, hours_of_worker_1: Decimal, hours_of_worker_2: Decimal
    ) -> None:
        """
        The certificates in the company accounts are equal to the worked hours * -1.
        The certificates in the member accounts are equal to the worked hours.
        They balance each other out.
        """
        self.register_hours_worked(hours_of_worker_1)
        self.register_hours_worked(hours_of_worker_2)
        stats = self.interactor.get_statistics()
        assert stats.certificates_count == Decimal(0)

    @parameterized.expand(
        [
            (
                Decimal(0),
                Decimal(5.2),
                Decimal(3.1),
            ),
            (
                Decimal(0.2),
                Decimal(5.2),
                Decimal(3.1),
            ),
        ]
    )
    def test_that_available_certificates_are_estimated_correctly_when_two_workers_have_worked_in_different_companies_with_varying_fic(
        self, base_fic: Decimal, hours_of_worker_1: Decimal, hours_of_worker_2: Decimal
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(
            target_fic=base_fic,
        )
        self.register_hours_worked(hours_of_worker_1)
        self.register_hours_worked(hours_of_worker_2)
        self.assertCertificatesAreEstimatedCorrectly()

    @parameterized.expand(
        [
            (Decimal(0), Decimal(2)),
            (Decimal(0.2), Decimal(3)),
            (Decimal(0.7), Decimal(2.5)),
            (Decimal(1), Decimal(6.1)),
        ]
    )
    def test_available_certificates_are_estimated_correctly_based_on_different_payout_factors_and_planned_labour_and_no_worked_hours(
        self,
        base_fic: Decimal,
        planned_labour: Decimal,
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(
            target_fic=base_fic,
        )
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=planned_labour,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
        )
        self.assertCertificatesAreEstimatedCorrectly()

    @parameterized.expand(
        [
            (Decimal(0), Decimal(10.5)),
            (Decimal(10.5), Decimal(10.5)),
            (Decimal(10.5), Decimal(5)),
            (Decimal(5), Decimal(10.5)),
            (Decimal(5), Decimal(5)),
        ]
    )
    def test_available_certificates_are_estimated_correctly_if_one_worker_worked_in_one_company_with_one_productive_plan(
        self,
        planned_labour: Decimal,
        worked_hours: Decimal,
    ) -> None:
        worker = self.member_generator.create_member()
        workplace = self.company_generator.create_company(workers=[worker])
        self.plan_generator.create_plan(
            planner=workplace,
            costs=ProductionCosts(
                labour_cost=planned_labour,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
        )
        self.register_hours_worked(
            company_and_worker=(workplace, worker),
            hours=worked_hours,
        )
        self.assertCertificatesAreEstimatedCorrectly()

    def register_hours_worked(
        self, hours: Decimal, company_and_worker: tuple[UUID, UUID] | None = None
    ) -> None:
        if hours == 0:
            return
        if hours < 0:
            raise ValueError("Hours worked cannot be negative")
        if company_and_worker is None:
            worker = self.member_generator.create_member()
            company = self.company_generator.create_company(workers=[worker])
        else:
            company, worker = company_and_worker
        self.registered_hours_worked_generator.register_hours_worked(
            company=company, worker=worker, hours=hours
        )

    def assertCertificatesAreEstimatedCorrectly(self) -> None:
        fic = self.fic_service.calculate_current_payout_factor()
        stats = self.interactor.get_statistics()
        certs_in_member_accounts = self._count_certs_in_member_accounts()
        certs_in_company_accounts = self._count_certs_in_company_accounts()
        self.assertAlmostEqual(
            stats.certificates_count,
            certs_in_member_accounts + certs_in_company_accounts * fic,
        )

    def _count_certs_in_member_accounts(self) -> Decimal:
        database_gateway = self.injector.get(DatabaseGateway)
        member_accounts = database_gateway.get_accounts().that_are_member_accounts()
        return decimal_sum(
            balance for _, balance in member_accounts.joined_with_balance()
        )

    def _count_certs_in_company_accounts(self) -> Decimal:
        database_gateway = self.injector.get(DatabaseGateway)
        company_accounts = database_gateway.get_accounts().that_are_labour_accounts()
        return decimal_sum(
            balance for _, balance in company_accounts.joined_with_balance()
        )


class CountAvailableProductTests(StatisticsBaseTestCase):
    def test_that_available_product_is_zero_when_no_plans_exist(self) -> None:
        stats = self.interactor.get_statistics()
        assert stats.available_product_in_productive_sector == 0

    def test_that_available_product_is_zero_when_no_productive_plans_exist(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=production_costs(2, 3, 4),
        )
        stats = self.interactor.get_statistics()
        assert stats.available_product_in_productive_sector == 0

    @parameterized.expand(
        [
            (production_costs(0, 0, 1), production_costs(0, 1, 2)),
            (production_costs(1, 2, 3), production_costs(4, 5, 6)),
        ]
    )
    def test_that_available_product_equals_accumulated_production_costs_of_productive_plans(
        self,
        costs_plan_1: ProductionCosts,
        costs_plan_2: ProductionCosts,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=costs_plan_1,
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=costs_plan_2,
        )
        stats = self.interactor.get_statistics()
        assert (
            stats.available_product_in_productive_sector
            == costs_plan_1.total_cost() + costs_plan_2.total_cost()
        )

    @parameterized.expand(
        [
            (Decimal(0), Decimal(0)),
            (Decimal(2), Decimal(0)),
            (Decimal(0), Decimal(3)),
            (Decimal(2), Decimal(3)),
        ]
    )
    def test_that_available_product_equals_planned_production_costs_of_productive_plans_ignoring_public_plans(
        self,
        planned_productive_costs: Decimal,
        planned_public_costs: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=production_costs(
                p=planned_productive_costs / 3,
                r=planned_productive_costs / 3,
                a=planned_productive_costs / 3,
            ),
        )
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=production_costs(
                p=planned_public_costs / 3,
                r=planned_public_costs / 3,
                a=planned_public_costs / 3,
            ),
        )
        stats = self.interactor.get_statistics()
        assert stats.available_product_in_productive_sector == planned_productive_costs

    @parameterized.expand(
        [
            (production_costs(2, 3, 4), 2, 0),
            (production_costs(2, 3, 4), 2, 1),
            (production_costs(2, 3, 4), 2, 2),
            (production_costs(2, 3, 4), 2, 3),
        ]
    )
    def test_that_available_product_is_what_is_left_after_consumption(
        self,
        production_costs: ProductionCosts,
        produced_quantities: int,
        consumed_quantities: int,
    ) -> None:
        plan = self.plan_generator.create_plan(
            amount=produced_quantities,
            costs=production_costs,
        )
        self.consumption_generator.create_private_consumption(
            plan=plan,
            amount=consumed_quantities,
        )
        stats = self.interactor.get_statistics()
        assert (
            stats.available_product_in_productive_sector
            == production_costs.total_cost()
            * (1 - Decimal(consumed_quantities / produced_quantities))
        )


class CountActivePlansTests(StatisticsBaseTestCase):
    def test_all_active_plans_are_counted(self) -> None:
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_count == 3

    def test_that_expired_plans_are_ignored(self) -> None:
        self.datetime_service.freeze_time()
        self.plan_generator.create_plan(
            timeframe=1,
        )
        self.plan_generator.create_plan(
            timeframe=1,
            is_public_service=True,
        )
        self.datetime_service.advance_time(
            timedelta(days=2),
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_count == 0


class CountActivePublicPlansTests(StatisticsBaseTestCase):
    def test_that_all_active_and_public_plans_are_counted(self) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 2

    def test_that_productive_plans_are_ignored(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 0

    def test_that_expired_public_plans_are_ignored(
        self,
    ) -> None:
        self.datetime_service.freeze_time()
        self.plan_generator.create_plan(
            is_public_service=True,
            timeframe=1,
        )
        self.datetime_service.advance_time(
            timedelta(days=2),
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 0


class CalculateAverageTimeframeTests(StatisticsBaseTestCase):
    def test_average_calculation_of_two_active_plan_timeframes(self) -> None:
        self.plan_generator.create_plan(timeframe=3)
        self.plan_generator.create_plan(timeframe=7)
        stats = self.interactor.get_statistics()
        assert stats.avg_timeframe == 5


class CalculatePlannedWorkTests(StatisticsBaseTestCase):
    def test_adding_up_planned_labour_of_two_plans(self) -> None:
        PLANNED_LABOUR_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(1, 1, PLANNED_LABOUR_PLAN_1),
        )
        PLANNED_LABOUR_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(1, 1, PLANNED_LABOUR_PLAN_2),
        )
        stats = self.interactor.get_statistics()
        assert stats.planned_work == PLANNED_LABOUR_PLAN_1 + PLANNED_LABOUR_PLAN_2

    def test_adding_up_resources_of_two_plans(self) -> None:
        PLANNED_RESOURCES_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(1, PLANNED_RESOURCES_PLAN_1, 1),
        )
        PLANNED_RESOURCES_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(1, PLANNED_RESOURCES_PLAN_2, 1),
        )
        stats = self.interactor.get_statistics()
        assert (
            stats.planned_resources
            == PLANNED_RESOURCES_PLAN_1 + PLANNED_RESOURCES_PLAN_2
        )

    def test_adding_up_means_of_two_plans(self) -> None:
        PLANNED_MEANS_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(PLANNED_MEANS_PLAN_1, 1, 1),
        )
        PLANNED_MEANS_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(PLANNED_MEANS_PLAN_2, 1, 1),
        )
        stats = self.interactor.get_statistics()
        assert stats.planned_means == PLANNED_MEANS_PLAN_1 + PLANNED_MEANS_PLAN_2


class CalculatePayoutFactorTests(StatisticsBaseTestCase):
    def test_that_payout_factor_is_available_even_without_plans_in_economy(
        self,
    ) -> None:
        stats = self.interactor.get_statistics()
        assert stats.payout_factor is not None


class CalculatePsfBalanceTests(StatisticsBaseTestCase):
    def test_that_psf_balance_is_available_even_without_plans_in_economy(
        self,
    ) -> None:
        stats = self.interactor.get_statistics()
        assert stats.psf_balance is not None
