from decimal import Decimal
from typing import Callable, Union

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, ProductOffer, Purchase
from arbeitszeit.purchase_factory import PurchaseFactory


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
