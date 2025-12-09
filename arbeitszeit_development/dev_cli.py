import os
from datetime import timedelta
from decimal import Decimal
from functools import wraps
from uuid import UUID

import click
from flask import current_app
from flask.cli import AppGroup

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.records import ProductionCosts
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.payout_factor import PayoutFactorService
from arbeitszeit_db import commit_changes
from arbeitszeit_db.db import Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from arbeitszeit_development.timeline_printer import TimelinePrinter
from arbeitszeit_flask.dependency_injection import FlaskModule
from tests.data_generators import (
    CompanyGenerator,
    ConsumptionGenerator,
    CooperationGenerator,
    MemberGenerator,
    PlanGenerator,
    WorkerAffiliationGenerator,
)
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.flask_integration.dependency_injection import FlaskTestingModule


def provide_dev_database_uri() -> str:
    return os.environ["ARBEITSZEITAPP_DEV_DB"]


def provide_database() -> Database:
    Database().configure(uri=provide_dev_database_uri())
    return Database()


class DevDatabaseModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(provide_database, is_singleton=True)
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)


class with_injection:
    def __init__(self) -> None:
        self._injector = Injector(
            [
                FlaskModule(),
                FlaskTestingModule(),
                DevDatabaseModule(),
                TestingModule(),
            ]
        )

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self._injector.call_with_injection(
                original_function, args=args, kwargs=kwargs
            )

        return wrapped_function

    @property
    def injector(self) -> Injector:
        return self._injector


fic = AppGroup(
    name="fic",
    help="""
    Commands related to the Factor of Individual Consumption (FIC).
    """,
)


@fic.command("calculate")
@with_injection()
def calculate_fic(payout_factor_service: PayoutFactorService) -> None:
    """Calculate and print the current FIC."""
    fic = payout_factor_service.calculate_current_payout_factor()
    click.echo(f"Current FIC: {fic}")


@fic.command("print-timeline")
@with_injection()
def print_timeline(
    datatime_service: DatetimeService,
    database_gateway: DatabaseGateway,
) -> None:
    """Print plans on a timeline along the fic calculation window."""
    WINDOW_LENGTH_DAYS = 180
    now = datatime_service.now()
    plans = list(database_gateway.get_plans().that_are_approved())
    tp = TimelinePrinter(
        now,
        plans,
        WINDOW_LENGTH_DAYS,
    )
    click.echo(tp.render())


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


@generate.command("member")
@click.option(
    "--name",
    "-n",
    help="Name of the member to be created.",
    type=str,
    default="Test Member",
    show_default=True,
)
@click.option(
    "--email",
    "-e",
    help="Email of the member to be created. If not given, a random email will be generated.",
    type=str,
)
@click.option(
    "--password",
    "-p",
    help="Password for the member.",
    type=str,
    default="password",
    show_default=True,
)
@commit_changes
@with_injection()
def generate_member(
    name: str, email: str | None, password: str, data_generator: MemberGenerator
) -> None:
    """Create a member."""
    member_id = data_generator.create_member(
        name=name,
        email=email if email else None,
        password=password,
    )
    click.echo(f"Member with ID {member_id} created.")


@generate.command("plan")
@click.option(
    "--name",
    "-n",
    help="Name of the plan to be created.",
    type=str,
    default="Test Plan",
    show_default=True,
)
@click.option(
    "--description",
    "-d",
    help="Description of the plan to be created.",
    type=str,
    default="This is a test plan.",
    show_default=True,
)
@click.option(
    "--production-unit",
    "-u",
    help="Description of the production unit.",
    type=str,
    default="1 Liter Bottle",
    show_default=True,
)
@click.option(
    "--planner",
    "-p",
    help="ID of the company who is the planner of the plan. If not given, a company will be created.",
    type=UUID,
)
@click.option(
    "--amount",
    "-a",
    help="Amount of the product to be produced.",
    type=int,
    default=100,
    show_default=True,
)
@click.option(
    "--labour-cost",
    "-lc",
    help="Labour cost.",
    type=Decimal,
    default=Decimal("1"),
    show_default=True,
)
@click.option(
    "--means-cost",
    "-mc",
    help="Fixed means cost.",
    type=Decimal,
    default=Decimal("1"),
    show_default=True,
)
@click.option(
    "--resource-cost",
    "-rc",
    help="Resource cost.",
    type=Decimal,
    default=Decimal("1"),
    show_default=True,
)
@click.option(
    "--timeframe",
    "-t",
    help="Timeframe of the plan in days.",
    type=int,
    default=14,
    show_default=True,
)
@click.option(
    "--is-public",
    "-i",
    help="Whether the plan is public service.",
    type=bool,
    default=False,
    show_default=True,
)
@click.option(
    "--backdate_days",
    "-b",
    help="Backdate start of plan for days.",
    type=int,
    default=0,
    show_default=True,
)
@commit_changes
@with_injection()
def generate_plan(
    name: str,
    description: str,
    production_unit: str,
    labour_cost: Decimal,
    means_cost: Decimal,
    resource_cost: Decimal,
    planner: UUID | None,
    amount: int,
    timeframe: int,
    is_public: bool,
    backdate_days: int,
    data_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
) -> None:
    """Create a plan."""
    costs = ProductionCosts(
        labour_cost=labour_cost,
        resource_cost=resource_cost,
        means_cost=means_cost,
    )
    now = datetime_service.now()
    datetime_service.freeze_time(now - timedelta(days=backdate_days))
    plan_id = data_generator.create_plan(
        amount=amount,
        product_name=name,
        description=description,
        is_public_service=is_public,
        production_unit=production_unit,
        costs=costs,
        planner=planner if planner else None,
        timeframe=timeframe,
    )
    datetime_service.freeze_time(now)
    datetime_service.unfreeze_time()
    click.echo(f"Plan with ID {plan_id} created.")


@generate.command("company")
@click.option(
    "--name",
    "-n",
    help="Name of the company to be created.",
    type=str,
    default="Test Company",
    show_default=True,
)
@click.option(
    "--email",
    "-e",
    help="Email of the company to be created. If not given, a random email will be generated.",
    type=str,
)
@click.option(
    "--password",
    "-p",
    help="Password for the company.",
    type=str,
    default="password",
    show_default=True,
)
@click.option(
    "--worker",
    "-w",
    help="ID of the member to be added as a worker. Can be repeated to add multiple workers.",
    type=UUID,
    multiple=True,
)
@commit_changes
@with_injection()
def generate_company(
    name: str,
    email: str | None,
    password: str,
    worker: tuple[UUID],
    data_generator: CompanyGenerator,
) -> None:
    """Create a company."""
    company_id = data_generator.create_company(
        name=name,
        email=email if email else None,
        password=password,
        workers=list(worker) if worker else None,
    )
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
    "--name",
    "-n",
    help="Name of the cooperation to be created.",
    type=str,
    default="Test Cooperation",
    show_default=True,
)
@click.option(
    "--coordinator",
    "-c",
    help="ID of the company who is the coordinator of the cooperation. If not given, a company will be created.",
    type=UUID,
)
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
    name: str,
    coordinator: UUID | None,
    plans: tuple[UUID],
    data_generator: CooperationGenerator,
) -> None:
    """Create a cooperation."""
    cooperation_id = data_generator.create_cooperation(
        name=name,
        plans=list(plans) if plans else None,
        coordinator=coordinator if coordinator else None,
    )
    click.echo(f"Cooperation with ID {cooperation_id} created.")


@generate.command("worker-company-affiliation")
@click.argument("company", type=UUID, nargs=1)
@click.argument("worker", type=UUID, nargs=-1)
@commit_changes
@with_injection()
def generate_company_worker_affiliation(
    company: UUID,
    worker: tuple[UUID],
    data_generator: WorkerAffiliationGenerator,
) -> None:
    """Create a worker-company affiliation."""
    if not worker:
        click.echo("No workers provided. Please provide at least one worker ID.")
        return

    data_generator.add_workers_to_company(
        company=company,
        workers=list(worker),
    )

    click.echo(
        f"Worker(s) {', '.join(str(w) for w in worker)} added to company {company}."
    )
