from dataclasses import dataclass
from decimal import Decimal

from arbeitszeit import records
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.payout_factor import PayoutFactorService
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService


@dataclass
class EconomicScenarios:
    plan_generator: PlanGenerator
    payout_factor_service: PayoutFactorService
    datetime_service: FakeDatetimeService
    database_gateway: DatabaseGateway

    def setup_environment_with_fic(self, target_fic: Decimal) -> None:
        """Sets up testing environment with plans that result in a specific FIC value

        Parameters:
            target_fic: The payout factor (FIC) to achieve. Must be between 0 and 1.

        We expect that there are no plans in the database and a FIC of 1 before this function is called.
        Be aware that this function will create two plans as a side effect.
        """
        assert (
            not self.database_gateway.get_plans()
        ), "There should be no plans in the database"
        assert self.payout_factor_service.calculate_current_payout_factor() == Decimal(
            1
        ), "Payout factor is not 1"
        if target_fic < 0 or target_fic > 1:
            raise ValueError("FIC must be between 0 and 1")
        elif target_fic == 1:
            # For FIC = 1, we just need a productive plan with no public plans
            self.plan_generator.create_plan(
                is_public_service=False,
                costs=records.ProductionCosts(
                    labour_cost=Decimal(1000),
                    means_cost=Decimal(0),
                    resource_cost=Decimal(0),
                ),
            )
            return

        # Choose reasonable default values for labor
        productive_labor = Decimal(1000)
        public_labor = Decimal(200)

        # Calculate required sum of fixed means and resources in public plan
        # Using the formula: fic = (L - (Po + Ro)) / (L + Lo)
        # Rearranged to: (Po + Ro) = L - fic * (L + Lo)
        required_public_means_and_resources = productive_labor - target_fic * (
            productive_labor + public_labor
        )

        # Divide evenly between means and resources (for simplicity)
        public_means = required_public_means_and_resources / 2
        public_resources = required_public_means_and_resources / 2

        # Create the productive plan
        self.plan_generator.create_plan(
            is_public_service=False,
            costs=records.ProductionCosts(
                labour_cost=productive_labor,
                means_cost=Decimal(0),  # Not relevant for FIC calculation
                resource_cost=Decimal(0),  # Not relevant for FIC calculation
            ),
        )

        # Create the public plan
        self.plan_generator.create_plan(
            is_public_service=True,
            costs=records.ProductionCosts(
                labour_cost=public_labor,
                means_cost=public_means,
                resource_cost=public_resources,
            ),
        )
        current_fic = self.payout_factor_service.calculate_current_payout_factor()
        assert round(current_fic, 7) == round(target_fic, 7)
