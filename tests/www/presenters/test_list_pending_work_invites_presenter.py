from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.use_cases import list_pending_work_invites as use_case
from arbeitszeit_web.www.presenters.list_pending_work_invites_presenter import (
    ListPendingWorkInvitesPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ListPendingWorkInvitesPresenterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.presenter = self.injector.get(ListPendingWorkInvitesPresenter)

    def test_no_invites_in_view_model_when_there_are_no_pending_invites(self) -> None:
        use_case_response = self.create_use_case_response([])
        view_model = self.presenter.present(use_case_response)
        assert not view_model.pending_invites

    @parameterized.expand([0, 1, 2])
    def test_correct_number_of_invites_shown_in_view_model(self, count: int) -> None:
        use_case_response = self.create_use_case_response(
            invite_details=[(uuid4(), "member name") for _ in range(count)]
        )
        view_model = self.presenter.present(use_case_response)
        assert len(view_model.pending_invites) == count

    def test_view_model_invite_has_member_id_from_use_case_response_as_string(
        self,
    ) -> None:
        member_id = uuid4()
        use_case_response = self.create_use_case_response(
            invite_details=[(member_id, "member name")]
        )
        view_model = self.presenter.present(use_case_response)
        assert view_model.pending_invites[0].member_id == str(member_id)

    @parameterized.expand(["some name", "some other name"])
    def test_view_model_invite_has_member_name_from_use_case_response(
        self, member_name: str
    ) -> None:
        use_case_response = self.create_use_case_response(
            invite_details=[(uuid4(), member_name)]
        )
        view_model = self.presenter.present(use_case_response)
        assert view_model.pending_invites[0].member_name == member_name

    def test_view_model_has_correct_navbar_items(self) -> None:
        use_case_response = self.create_use_case_response([])
        view_model = self.presenter.present(use_case_response)
        assert view_model.navbar_items[0].text == self.translator.gettext("Workers")
        assert (
            view_model.navbar_items[0].url
            == self.url_index.get_invite_worker_to_company_url()
        )
        assert view_model.navbar_items[1].text == self.translator.gettext(
            "Pending work invites"
        )
        assert view_model.navbar_items[1].url is None

    def create_use_case_response(
        self, invite_details: list[tuple[UUID, str]]
    ) -> use_case.Response:
        return use_case.Response(
            pending_invites=[
                use_case.PendingInvite(member_id, member_name)
                for member_id, member_name in invite_details
            ]
        )
