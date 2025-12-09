import enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.services.payout_factor import PayoutFactorService
from arbeitszeit_development.timeline_printer import TimelinePrinter
from tests.interactors.base_test_case import BaseTestCase


class PayoutFactorServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)

    def test_that_payout_factor_is_1_if_no_plans_exist(self) -> None:
        pf = self.service.calculate_current_payout_factor()
        assert pf == 1

    def test_that_payout_factor_is_1_if_there_is_only_one_public_plan_without_costs(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts.zero(),
        )
        pf = self.service.calculate_current_payout_factor()
        assert pf == 1

    @parameterized.expand(
        [
            (Decimal(1), Decimal(0), Decimal(1)),
            (Decimal(1), Decimal(1), Decimal(0)),
            (Decimal(1), Decimal(0), Decimal(0)),
            (Decimal(1), Decimal(1), Decimal(1)),
            (Decimal(0), Decimal(0), Decimal(1)),
            (Decimal(0), Decimal(1), Decimal(0)),
            (Decimal(0), Decimal(1), Decimal(1)),
        ]
    )
    def test_that_payout_factor_is_0_if_there_is_only_one_public_plan_with_costs(
        self,
        public_a: Decimal,
        public_p: Decimal,
        public_r: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(public_a, public_p, public_r),
        )
        pf = self.service.calculate_current_payout_factor()
        assert pf == 0

    def test_that_payout_factor_is_0_when_productive_labour_equals_sum_of_public_p_and_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(20), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_current_payout_factor()
        assert pf == 0

    def test_that_payout_factor_is_positive_when_productive_labour_surpasses_sum_of_public_p_and_r(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(21), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_current_payout_factor()
        assert pf > 0

    def test_that_payout_factor_is_zero_when_sum_of_public_p_and_r_surpasses_productive_labour(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(Decimal(0), Decimal(10), Decimal(10)),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(Decimal(19), Decimal(0), Decimal(0)),
        )
        pf = self.service.calculate_current_payout_factor()
        assert pf == 0

    @parameterized.expand(
        [
            (Decimal(10), Decimal(10), Decimal(10), Decimal(10), Decimal(0)),
            (Decimal(20), Decimal(10), Decimal(10), Decimal(10), Decimal(0)),
            (Decimal(30), Decimal(10), Decimal(10), Decimal(10), Decimal(0.25)),
            (Decimal(30), Decimal(0), Decimal(0), Decimal(0), Decimal(1)),
        ]
    )
    def test_that_expected_payout_factor_gets_calculated(
        self,
        productive_a: Decimal,
        public_a: Decimal,
        public_p: Decimal,
        public_r: Decimal,
        expected_payout_factor: Decimal,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=ProductionCosts(public_a, public_r, public_p),
        )
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=ProductionCosts(productive_a, Decimal(10), Decimal(10)),
        )
        pf = self.service.calculate_current_payout_factor()
        self.assertAlmostEqual(pf, expected_payout_factor)


WINDOW_SIZE = 180
DEFAULT_COSTS = ProductionCosts(
    means_cost=Decimal(1), resource_cost=Decimal(1), labour_cost=Decimal(1)
)


class PlanPosition(enum.Enum):
    """
    The plan's position on a timeline relative to a gliding window's borders.
    """

    outside_of_left_border = enum.auto()
    one_half_outside_of_left_border = enum.auto()
    inside = enum.auto()
    one_half_outside_of_right_border = enum.auto()
    outside_of_both_borders = enum.auto()


@dataclass
class PlanConfig:
    position: PlanPosition
    is_public: bool = False
    costs: ProductionCosts = field(default_factory=lambda: DEFAULT_COSTS)


@dataclass
class OnePlanTestCase:
    plan: PlanConfig
    expected_payout_factor: Decimal


@dataclass
class TwoPlanTestCase:
    plan_1: PlanConfig
    plan_2: PlanConfig
    expected_payout_factor: Decimal


ONE_PLAN_TEST_CASES = [
    OnePlanTestCase(
        plan=PlanConfig(
            position=PlanPosition.outside_of_left_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            is_public=True,
            position=PlanPosition.outside_of_left_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            position=PlanPosition.one_half_outside_of_left_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            is_public=True,
            position=PlanPosition.one_half_outside_of_left_border,
        ),
        expected_payout_factor=Decimal(0),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            position=PlanPosition.inside,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            is_public=True,
            position=PlanPosition.inside,
        ),
        expected_payout_factor=Decimal(0),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            position=PlanPosition.one_half_outside_of_right_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            is_public=True,
            position=PlanPosition.one_half_outside_of_right_border,
        ),
        expected_payout_factor=Decimal(0),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            position=PlanPosition.outside_of_both_borders,
        ),
        expected_payout_factor=Decimal(1),
    ),
    OnePlanTestCase(
        plan=PlanConfig(
            is_public=True,
            position=PlanPosition.outside_of_both_borders,
        ),
        expected_payout_factor=Decimal(0),
    ),
]


TWO_PLAN_TEST_CASES: list[TwoPlanTestCase] = [
    TwoPlanTestCase(
        plan_1=PlanConfig(
            position=PlanPosition.outside_of_left_border,
        ),
        plan_2=PlanConfig(
            is_public=True,
            position=PlanPosition.outside_of_left_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            is_public=True,
            position=PlanPosition.one_half_outside_of_left_border,
        ),
        expected_payout_factor=Decimal(0),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            is_public=True,
            position=PlanPosition.inside,
        ),
        expected_payout_factor=Decimal(0),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            is_public=True,
            position=PlanPosition.one_half_outside_of_right_border,
        ),
        expected_payout_factor=Decimal(0),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(is_public=True, position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            position=PlanPosition.one_half_outside_of_left_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(is_public=True, position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            position=PlanPosition.inside,
        ),
        expected_payout_factor=Decimal(1),
    ),
    TwoPlanTestCase(
        plan_1=PlanConfig(is_public=True, position=PlanPosition.outside_of_left_border),
        plan_2=PlanConfig(
            position=PlanPosition.one_half_outside_of_right_border,
        ),
        expected_payout_factor=Decimal(1),
    ),
]


class PayoutFactorTests(BaseTestCase):
    """
    Run these tests with pytest options "-vs" to see graphical timeline output for
    debugging purposes.
    """

    def setUp(self):
        super().setUp()
        self.service = self.injector.get(PayoutFactorService)

    @parameterized.expand(
        [(tc.plan, tc.expected_payout_factor) for tc in ONE_PLAN_TEST_CASES],
        name_func=lambda func, num, p: f"{func.__name__}__{'public' if p.args[0].is_public else 'productive'}__{p.args[0].position.name}",
    )
    def test_that_expected_payout_factor_is_calculated_correctly_with_one_plan_in_economy(
        self,
        plan: PlanConfig,
        expected_payout_factor: Decimal,
    ) -> None:
        self._create_plan(plan)
        self._print_timeline()
        pf = self.service.calculate_current_payout_factor()
        assert pf == expected_payout_factor

    @parameterized.expand(
        [
            (tc.plan_1, tc.plan_2, tc.expected_payout_factor)
            for tc in TWO_PLAN_TEST_CASES
        ],
        name_func=lambda func, num, p: f"{func.__name__}__{'pub' if p.args[0].is_public else 'prod'}_{p.args[0].position.name}__{'pub' if p.args[1].is_public else 'prod'}_{p.args[1].position.name}",
    )
    def test_that_expected_payout_factor_is_calculated_correctly_with_two_plans_in_economy(
        self,
        plan_1: PlanConfig,
        plan_2: PlanConfig,
        expected_payout_factor: Decimal,
    ) -> None:
        self._create_plan(plan_1)
        self._create_plan(plan_2)
        self._print_timeline()
        pf = self.service.calculate_current_payout_factor()
        assert pf == expected_payout_factor

    def _create_plan(self, plan: PlanConfig) -> None:
        now = datetime(2025, 12, 1)
        self.datetime_service.freeze_time(now)
        plan_timeframe, plan_start = self._calculate_plan_duration_and_start(
            plan.position
        )
        self.datetime_service.freeze_time(plan_start)
        self.plan_generator.create_plan(
            is_public_service=plan.is_public,
            costs=plan.costs,
            timeframe=plan_timeframe,
        )
        self.datetime_service.freeze_time(now)

    def _calculate_plan_duration_and_start(
        self, plan_position: PlanPosition
    ) -> tuple[int, datetime]:
        now = self.datetime_service.now()
        match plan_position:
            case PlanPosition.outside_of_left_border:
                plan_duration = WINDOW_SIZE
                plan_start = now - timedelta(days=WINDOW_SIZE * 3)
            case PlanPosition.one_half_outside_of_left_border:
                plan_duration = WINDOW_SIZE
                plan_start = now - timedelta(days=WINDOW_SIZE)
            case PlanPosition.inside:
                plan_duration = WINDOW_SIZE // 4
                plan_start = now
            case PlanPosition.one_half_outside_of_right_border:
                plan_duration = WINDOW_SIZE
                plan_start = now
            case PlanPosition.outside_of_both_borders:
                plan_duration = WINDOW_SIZE * 2
                plan_start = now - timedelta(days=WINDOW_SIZE)
        return int(plan_duration), plan_start

    def _print_timeline(self) -> None:
        """TEMPORARY: Print timeline for debugging purposes."""
        plans = list(self.database_gateway.get_plans())
        printer = TimelinePrinter(
            now=self.datetime_service.now(),
            plans=plans,
            window_size=WINDOW_SIZE,
        )
        printer.print_timeline()
