from datetime import datetime

import pytest

from arbeitszeit.use_cases import CreateOffer, CreateOfferRequest
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
    with pytest.raises(AssertionError, match="Plan is inactive."):
        create_offer(offer_request)
    assert len(offer_repository.offers) == 0


@injection_test
def test_that_response_returns_correct_offer_name_and_description(
    create_offer: CreateOffer,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer_request = CreateOfferRequest("expected name", "expected description", plan.id)
    response = create_offer(offer_request)
    assert response.name == "expected name"
    assert response.description == "expected description"
