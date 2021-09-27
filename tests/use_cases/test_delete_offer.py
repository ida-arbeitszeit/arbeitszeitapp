from datetime import datetime
from typing import List
from uuid import uuid4

import pytest

from arbeitszeit.entities import ProductOffer
from arbeitszeit.use_cases import CreateOfferResponse, DeleteOffer, DeleteOfferRequest
from tests.data_generators import OfferGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import OfferRepository


def offer_in_offers(offer: CreateOfferResponse, offers: List[ProductOffer]) -> bool:
    for o in offers:
        if o.id == offer.id:
            return True
    return False


@injection_test
def test_that_offer_gets_deleted(
    offer_repo: OfferRepository,
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer = offer_generator.create_offer(plan=plan)
    assert len(offer_repo.offers) == 1
    assert offer.id
    delete_offer(DeleteOfferRequest(plan.planner.id, offer.id))
    assert len(offer_repo.offers) == 0


@injection_test
def test_that_correct_offer_gets_deleted(
    offer_repo: OfferRepository,
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer1 = offer_generator.create_offer(plan=plan)
    offer2 = offer_generator.create_offer(plan=plan)
    offer3 = offer_generator.create_offer(plan=plan)
    assert len(offer_repo.offers) == 3
    assert offer1.id
    delete_offer(DeleteOfferRequest(plan.planner.id, offer1.id))
    assert len(offer_repo.offers) == 2
    assert not offer_in_offers(offer1, offer_repo.offers)
    assert offer_in_offers(offer2, offer_repo.offers)
    assert offer_in_offers(offer3, offer_repo.offers)


@injection_test
def test_that_offer_does_not_get_deleted_when_planner_is_not_equal_to_requester_of_deletion(
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
    offer_repository: OfferRepository,
):
    plan1 = plan_generator.create_plan(activation_date=datetime.min)
    plan2 = plan_generator.create_plan(activation_date=datetime.min)
    offer = offer_generator.create_offer(plan=plan2)
    assert len(offer_repository.offers) == 1
    assert offer.id
    delete_offer(DeleteOfferRequest(plan1.planner.id, offer.id))
    assert len(offer_repository.offers) == 1


@injection_test
def test_that_correct_offer_id_is_shown_after_deletion_of_offer(
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer = offer_generator.create_offer(plan=plan)
    assert offer.id
    response = delete_offer(DeleteOfferRequest(plan.planner.id, offer.id))
    assert response.offer_id == offer.id


@injection_test
def test_that_success_is_true_is_shown_when_offer_gets_deleted(
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    offer = offer_generator.create_offer(plan=plan)
    assert offer.id
    response = delete_offer(DeleteOfferRequest(plan.planner.id, offer.id))
    assert response.is_success == True


@injection_test
def test_that_success_is_false_is_shown_when_offer_does_not_get_deleted(
    delete_offer: DeleteOffer,
    offer_generator: OfferGenerator,
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan(activation_date=datetime.min)
    plan2 = plan_generator.create_plan(activation_date=datetime.min)
    offer = offer_generator.create_offer(plan=plan2)
    assert offer.id
    response = delete_offer(DeleteOfferRequest(plan1.planner.id, offer.id))
    assert response.is_success == False


@injection_test
def test_that_exception_is_raised_when_trying_to_delete_a_nonexisting_offer(
    delete_offer: DeleteOffer,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    with pytest.raises(Exception):
        delete_offer(DeleteOfferRequest(plan.planner.id, uuid4()))
