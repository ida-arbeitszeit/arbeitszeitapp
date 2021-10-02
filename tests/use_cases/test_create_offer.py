from datetime import datetime

from arbeitszeit.use_cases import CreateOffer, CreateOfferRequest
from arbeitszeit.use_cases.create_offer import RejectionReason
from tests.data_generators import PlanGenerator
from tests.use_cases.repositories import OfferRepository

from .dependency_injection import injection_test


@injection_test
def test_that_create_offer_creates_an_offer(
    create_offer: CreateOffer,
    offer_repository: OfferRepository,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer_request = CreateOfferRequest(plan.prd_name, plan.description, plan.id)
    assert len(offer_repository.offers) == 0
    create_offer(offer_request)
    assert len(offer_repository.offers) == 1


@injection_test
def test_that_create_offer_does_not_create_an_offer_when_plan_is_not_active(
    create_offer: CreateOffer,
    offer_repository: OfferRepository,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=None)
    offer_request = CreateOfferRequest(plan.prd_name, plan.description, plan.id)
    create_offer(offer_request)
    assert len(offer_repository.offers) == 0


@injection_test
def test_that_correct_response_is_returned_when_plan_is_inactive(
    create_offer: CreateOffer,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=None)
    offer_request = CreateOfferRequest(plan.prd_name, plan.description, plan.id)
    response = create_offer(offer_request)
    assert response.is_created is False
    assert response.rejection_reason == RejectionReason.plan_inactive
