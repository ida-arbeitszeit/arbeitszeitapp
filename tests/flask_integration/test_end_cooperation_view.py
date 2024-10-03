from uuid import uuid4

from tests.data_generators import CooperationGenerator, PlanGenerator

from .flask import ViewTestCase

URL = "/company/end_cooperation"


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company = self.login_company()

    def test_404_is_returned_when_no_form_data_is_sent(
        self,
    ) -> None:
        data: dict = {}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_plan_does_not_exist(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        data = {"plan_id": str(uuid4()), "cooperation_id": str(cooperation)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_coop_does_not_exist(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        data = {"plan_id": str(plan), "cooperation_id": str(uuid4())}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_404_is_returned_when_coop_and_plan_do_exist_but_requester_is_neither_planner_nor_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(plans=[plan])
        data = {"plan_id": str(plan), "cooperation_id": str(cooperation)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 404

    def test_302_is_returned_when_coop_and_plan_do_exist_and_requester_is_planner(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(planner=self.company.id)
        cooperation = self.cooperation_generator.create_cooperation(plans=[plan])
        data = {"plan_id": str(plan), "cooperation_id": str(cooperation)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 302

    def test_302_is_returned_when_coop_and_plan_do_exist_and_requester_is_coordinator(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            plans=[plan], coordinator=self.company
        )
        data = {"plan_id": str(plan), "cooperation_id": str(cooperation)}
        response = self.client.post(URL, data=data)
        assert response.status_code == 302
