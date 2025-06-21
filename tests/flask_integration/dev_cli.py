from decimal import Decimal
from uuid import UUID

import click
from flask import current_app
from flask.cli import AppGroup

from arbeitszeit.records import ProductionCosts
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import with_injection
from tests.data_generators import (
    CompanyGenerator,
    ConsumptionGenerator,
    CooperationGenerator,
    PlanGenerator,
)

generate = AppGroup(
    name="generate",
    help="""
    Generate test data for the development database. Internally, these commands make
    use of the data generators, which in turn use the domain logic to create the data.

    The ARBEITSZEITAPP_CONFIGURATION_PATH is used to derive the database connection
    string and other configuration options.

    Run `flask generate COMMAND --help` for more information on a specific command.
    """,
)


@generate.command("plan")
@click.option(
    "--labour-cost",
    "-l",
    help="Labour cost.",
    type=Decimal,
)
@commit_changes
@with_injection()
def generate_plan(labour_cost: Decimal | None, data_generator: PlanGenerator) -> None:
    """Create a plan."""
    if labour_cost:
        costs = ProductionCosts(
            labour_cost=labour_cost,
            resource_cost=Decimal("0"),
            means_cost=Decimal("0"),
        )
    else:
        costs = None
    plan_id = data_generator.create_plan(
        costs=costs,
    )
    click.echo(f"Plan with ID {plan_id} created.")


@generate.command("company")
@commit_changes
@with_injection()
def generate_company(data_generator: CompanyGenerator) -> None:
    """Create a company."""
    company_id = data_generator.create_company()
    click.echo(f"Company with ID {company_id} created.")


@generate.command("private-consumption")
@click.option(
    "--plan",
    "-p",
    help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
    type=UUID,
)
@commit_changes
@with_injection()
def generate_private_consumption(
    plan: UUID | None,
    data_generator: ConsumptionGenerator,
) -> None:
    """
    Create a private consumption.
    """
    current_app.config["ALLOWED_OVERDRAW_MEMBER"] = "unlimited"
    data_generator.create_private_consumption(
        plan=plan,
    )
    click.echo("Private consumption created.")


@generate.command("productive-consumption-of-r")
@click.option(
    "--plan",
    "-p",
    help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
    type=UUID,
)
@commit_changes
@with_injection()
def generate_productive_consumption_of_r(
    plan: UUID | None,
    data_generator: ConsumptionGenerator,
) -> None:
    """
    Create a productive consumption of raw materials.
    """
    data_generator.create_resource_consumption_by_company(
        plan=plan,
    )
    click.echo("Productive consumption created.")


@generate.command("productive-consumption-of-p")
@click.option(
    "--plan",
    "-p",
    help="ID of plan to be consumed. If no plan is given, a plan will be created automatically.",
    type=UUID,
)
@commit_changes
@with_injection()
def generate_productive_consumption_of_p(
    plan: UUID | None,
    data_generator: ConsumptionGenerator,
) -> None:
    """
    Create a productive consumption of fixed means.
    """
    data_generator.create_fixed_means_consumption(
        plan=plan,
    )
    click.echo("Productive consumption created.")


@generate.command("cooperation")
@click.option(
    "--plans",
    "-p",
    help="ID of plan to be included in the cooperation. Can be repeated to include multiple plans.",
    multiple=True,
    type=UUID,
)
@commit_changes
@with_injection()
def generate_cooperation(
    plans: tuple[UUID],
    data_generator: CooperationGenerator,
) -> None:
    """Create a cooperation."""
    cooperation_id = data_generator.create_cooperation(
        plans=list(plans) if plans else None
    )
    click.echo(f"Cooperation with ID {cooperation_id} created.")
