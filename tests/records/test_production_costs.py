from decimal import Decimal
from unittest import TestCase

from arbeitszeit.records import ProductionCosts


class ArithmeticTests(TestCase):
    def test_dividing_costs_by_two_halfs_every_component_of_the_costs(self) -> None:
        costs = ProductionCosts(
            labour_cost=Decimal(5),
            resource_cost=Decimal(6),
            means_cost=Decimal(7),
        )
        halfed_costs = costs / 2
        self.assertEqual(
            halfed_costs.labour_cost,
            costs.labour_cost / 2,
        )
        self.assertEqual(
            halfed_costs.means_cost,
            costs.means_cost / 2,
        )
        self.assertEqual(
            halfed_costs.resource_cost,
            costs.resource_cost / 2,
        )

    def test_dividing_costs_by_zero_point_5_doubles_cost_components(self) -> None:
        costs = ProductionCosts(
            labour_cost=Decimal(5),
            resource_cost=Decimal(6),
            means_cost=Decimal(7),
        )
        halfed_costs = costs / 0.5
        self.assertEqual(
            halfed_costs.labour_cost,
            costs.labour_cost * 2,
        )
        self.assertEqual(
            halfed_costs.means_cost,
            costs.means_cost * 2,
        )
        self.assertEqual(
            halfed_costs.resource_cost,
            costs.resource_cost * 2,
        )

    def test_adding_costs_adds_their_components(self) -> None:
        costs_1 = ProductionCosts(
            labour_cost=Decimal(1),
            resource_cost=Decimal(2),
            means_cost=Decimal(3),
        )
        costs_2 = ProductionCosts(
            labour_cost=Decimal(4),
            resource_cost=Decimal(5),
            means_cost=Decimal(6),
        )
        sum_costs = costs_1 + costs_2
        self.assertEqual(
            sum_costs.labour_cost,
            costs_1.labour_cost + costs_2.labour_cost,
        )
        self.assertEqual(
            sum_costs.means_cost,
            costs_1.means_cost + costs_2.means_cost,
        )
        self.assertEqual(
            sum_costs.resource_cost,
            costs_1.resource_cost + costs_2.resource_cost,
        )
