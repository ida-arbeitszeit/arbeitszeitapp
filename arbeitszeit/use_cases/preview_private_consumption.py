from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    plan: UUID | None = None
    amount: int | None = None


@dataclass
class ProductInformation:
    name: str | None = None
    description: str | None = None


@dataclass
class Response:
    product: ProductInformation | None = None
    total_cost: Decimal | None = None


@dataclass
class PreviewPrivateConsumptionUseCase:
    database: DatabaseGateway

    def preview_private_consumption(self, request: Request) -> Response:
        if not request.plan:
            return Response()
        plan = self.database.get_plans().with_id(request.plan).first()
        if not plan:
            return Response()
        product = ProductInformation(
            name=plan.prd_name,
            description=plan.description,
        )
        if request.amount is None or request.amount <= 0:
            return Response(product=product)
        total_cost = plan.production_costs.total_cost() * request.amount
        return Response(
            product=product,
            total_cost=total_cost,
        )
