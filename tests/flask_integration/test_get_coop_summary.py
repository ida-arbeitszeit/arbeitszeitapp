from uuid import uuid4

from tests.data_generators import CooperationGenerator

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.coop_generator = self.injector.get(CooperationGenerator)
        self.member, _, self.email = self.login_member()
        self.member = self.confirm_member(member=self.member, email=self.email)

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
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)

    def test_get_404_when_coop_does_not_exist(self) -> None:
        url = f"/company/cooperation_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_coop_exists(self) -> None:
        coop = self.coop_generator.create_cooperation()
        url = f"/company/cooperation_summary/{coop.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
