from decimal import Decimal
from typing import Callable, Union

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, Plan, ProductOffer, Purchase, SocialAccounting
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.plan_factory import PlanFactory


def purchase_product(
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
    return purchase


def create_plan(
    datetime_service: DatetimeService,
    planner: Company,
    social_accounting: SocialAccounting,
    costs_p: Decimal,
    costs_r: Decimal, 
    costs_a: Decimal,  
    prd_name: str,
    prd_unit: str,
    prd_amount: int, 
    description: str,
    timeframe: int,
    plan_factory: PlanFactory,
) -> Plan:
    plan = plan_factory.create_plan(
        plan_creation_date=datetime_service.now(),
        planner=planner,
        social_accounting=social_accounting,
        costs_p=costs_p,
        costs_r=costs_r, 
        costs_a=costs_a,  
        prd_name=prd_name,
        prd_unit=prd_unit,
        prd_amount=prd_amount, 
        description=description,
        timeframe=timeframe,
    )
    return plan