from uuid import uuid4

from arbeitszeit.use_cases import ListedPlan
from arbeitszeit_web.list_plans import ListPlansPresenter, ListPlansResponse

fake_response_with_one_plan = ListPlansResponse(
    plans=[ListedPlan(id=uuid4(), prd_name="fake prd name")]
)


def test_presenter_shows_empty_list_of_plans():
    presenter = ListPlansPresenter()
    presentation = presenter.present(ListPlansResponse(plans=[]))
    assert not presentation.plans


def test_presenter_shows_one_plan():
    presenter = ListPlansPresenter()
    presentation = presenter.present(fake_response_with_one_plan)
    assert presentation.plans


def test_presenter_shows_correct_info_of_one_plan():
    presenter = ListPlansPresenter()
    presentation = presenter.present(fake_response_with_one_plan)
    assert len(presentation.plans) == 1
    assert presentation.plans[0].id == str(fake_response_with_one_plan.plans[0].id)
    assert presentation.plans[0].prd_name == "fake prd name"
