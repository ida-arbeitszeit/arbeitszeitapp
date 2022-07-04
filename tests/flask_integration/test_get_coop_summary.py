from uuid import uuid4

from tests.data_generators import CooperationGenerator

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.member = self.login_member()

    def test_get_404_when_coop_does_not_exist(self) -> None:
        url = f"/member/cooperation_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_coop_exists(self) -> None:
        coop = self.coop_generator.create_cooperation()
        url = f"/member/cooperation_summary/{coop.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.company = self.login_company()

    def test_get_404_when_coop_does_not_exist(self) -> None:
        url = f"/company/cooperation_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_coop_exists(self) -> None:
        coop = self.coop_generator.create_cooperation()
        url = f"/company/cooperation_summary/{coop.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
