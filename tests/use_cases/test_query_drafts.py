from arbeitszeit.entities import PlanDraft
from arbeitszeit.use_cases import ListDraftsOfCompany, ListDraftsResponse
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test


def draft_in_results(draft: PlanDraft, response: ListDraftsResponse) -> bool:
    return draft.id in [draft.id for draft in response.results]


@injection_test
def test_that_no_draft_is_returned_when_searching_an_empty_repo(
    list_drafts: ListDraftsOfCompany,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company_entity()
    results = list_drafts(company.id).results
    assert not results


@injection_test
def test_that_only_drafts_from_company_are_returned(
    list_drafts: ListDraftsOfCompany,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()
    draft1 = plan_generator.draft_plan(planner=company1)
    draft2 = plan_generator.draft_plan(planner=company2)
    response = list_drafts(company1.id)
    assert draft_in_results(draft1, response)
    assert not draft_in_results(draft2, response)


@injection_test
def test_that_draft_description_is_returned(
    list_drafts: ListDraftsOfCompany,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company_entity()
    plan_generator.draft_plan(planner=company, description="test description")
    response = list_drafts(company.id)
    assert response.results.pop().description == "test description"
