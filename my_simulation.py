from cli_app.simulation import Sim
from tests.use_cases.dependency_injection import get_dependency_injector
from tests.data_generators import CompanyGenerator, PlanGenerator
from arbeitszeit.repositories import CompanyRepository, PlanRepository
from datetime import datetime
from arbeitszeit.price_calculator import calculate_price

injector = get_dependency_injector()

company_repo = injector.get(CompanyRepository)
plan_repo = injector.get(PlanRepository)

company_gen = injector.get(CompanyGenerator)
plan_gen = injector.get(PlanGenerator)


def create_special_company(report):
    company_gen.create_company(name="special one gmbh", email="check@gmx.de")


def create_company(report):
    company_gen.create_company()


def analyse_number_of_companies(report):
    count = company_repo.count_registered_companies()
    report.string(f"all companies: {count}")


def special_company_creates_plan(report, ts):
    company = list(company_repo.query_companies_by_email("check@gmx.de"))[0]
    plan = plan_gen.create_plan(
        planner=company,
        product_name="a very special product",
        activation_date=ts.now(),
    )
    report.string(f"activation date: {plan.activation_date}")


def all_companies_create_plans(report, ts):
    companies = company_repo.get_all_companies()
    for comp in companies:
        plan_gen.create_plan(
            planner=comp,
            product_name="a generic product",
            activation_date=ts.now(),
        )


def count_all_active_plans(report):
    plans = list(plan_repo.all_active_plans())
    report.string(f"number of active plans: {len(plans)}")


def calculate_mean_price(report):
    plans = plan_repo.all_active_plans()
    prices = []
    for plan in plans:
        prices.append(calculate_price([plan]))
    report.string(f"Mean price = {sum(prices) / len(prices)}")


def run():
    sim = Sim()

    ev_create_company = sim.event(create_company, "company created")
    ev_create_special_company = sim.event(
        create_special_company, "special company created"
    )
    ev_analyse_number_of_companies = sim.event(
        analyse_number_of_companies, "analysing registered companies"
    )
    ev_count_all_active_plans = sim.event(
        count_all_active_plans, "count all active plans"
    )
    ev = sim.event(
        special_company_creates_plan,
        "special company creates plan",
        ([sim.time_service]),
    )

    sim.set_time(datetime(1984, 2, 19, 5))
    sim.enqueue_event(ev_create_special_company)
    for i in range(3):
        sim.enqueue_event(ev_create_company)
        sim.enqueue_event(ev_create_company)
        sim.enqueue_event(ev_create_special_company)
        sim.enqueue_event(ev)
        sim.enqueue_event(ev_create_company)
        sim.enqueue_event(ev_analyse_number_of_companies)
        sim.enqueue_event(ev_count_all_active_plans)
        sim.skip_time(days=14)
        if i == 2:
            sim.interact()
        sim.comment("=======")

    sim.create_report()
    sim.run()


if __name__ == "__main__":
    run()
