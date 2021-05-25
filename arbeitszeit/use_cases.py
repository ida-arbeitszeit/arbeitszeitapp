from decimal import Decimal
from typing import Callable, Union

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.errors import WorkerAlreadyAtCompany
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import CompanyWorkerRepository, PurchaseRepository
from arbeitszeit.entities import Company, Member, Plan, ProductOffer, Purchase, SocialAccounting
from arbeitszeit.plan_factory import PlanFactory


def purchase_product(
    purchase_repository: PurchaseRepository,
    datetime_service: DatetimeService,
    lookup_koop_price: Callable[[ProductOffer], Decimal],
    lookup_product_provider: Callable[[ProductOffer], Company],
    product_offer: ProductOffer,
    buyer: Union[Member, Company],
    purchase_factory: PurchaseFactory,
) -> Purchase:
    price = lookup_koop_price(product_offer)
    purchase = purchase_factory.create_private_purchase(
        purchase_date=datetime_service.now(),
        product_offer=product_offer,
        buyer=buyer,
        price=price,
    )
    product_offer.deactivate()
    provider = lookup_product_provider(product_offer)
    provider.increase_credit(price)
    buyer.reduce_credit(price)
    purchase_repository.add(purchase)
    return purchase


def add_worker_to_company(
    company_worker_repository: CompanyWorkerRepository,
    company: Company,
    worker: Member,
) -> None:
    """This function may raise a WorkerAlreadyAtCompany exception if the
    worker is already employed at the company."""
    company_workers = company_worker_repository.get_company_workers(company)
    if worker.id in [worker.id for worker in company_workers]:
        raise WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)

    
def create_plan(
    id: int,
    datetime_service: DatetimeService,
    planner: Company,
    costs_p: Decimal,
    costs_r: Decimal, 
    costs_a: Decimal,  
    prd_name: str,
    prd_unit: str,
    prd_amount: int, 
    description: str,
    timeframe: int,
    plan_factory: PlanFactory,
    social_accounting: SocialAccounting,
    approved: bool,
    approval_date: DatetimeService,
    approval_reason: str,
) -> Plan:
    plan = plan_factory.create_plan(
        id=id,
        plan_creation_date=datetime_service.now(),
        planner=planner,
        costs_p=costs_p,
        costs_r=costs_r, 
        costs_a=costs_a,  
        prd_name=prd_name,
        prd_unit=prd_unit,
        prd_amount=prd_amount, 
        description=description,
        timeframe=timeframe,
        social_accounting=social_accounting,
        approved=approved,
        approval_date=approval_date,
        approval_reason=approval_reason,
    )
    return plan


def seeking_approval(
    datetime_service: DatetimeService,
    plan: Plan,
) -> Plan:
    approval_seeker = plan.planner
    approved = True if True else False  # criteria for approval_seeker to be defined
    reason = None if approved else "Nicht genug Kredit."
    plan.approved = True
    plan.approval_date = datetime_service.now()
    plan.approval_reason = reason
    return plan
 

def granting_credit():
    ...