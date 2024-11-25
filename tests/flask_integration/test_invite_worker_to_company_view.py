from uuid import uuid4

from parameterized import parameterized

from tests.company import CompanyManager

from .flask import ViewTestCase

URL = "/company/invite_worker_to_company"


class AnonymousUserTests(ViewTestCase):
    def test_get_redirected_when_not_logged_in(self) -> None:
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 302)


class InviteWorkerToCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_get_yields_200_when_logged_in_as_company(self) -> None:
        self.login_company()
        response = self.client.get(URL)
        assert response.status_code == 200

    @parameterized.expand(
        [
            ("test member 123",),
            ("test member 456",),
        ]
    )
    def test_that_get_response_contains_worker_name_of_worker_that_works_there(
        self, worker_name: str
    ) -> None:
        company = self.login_company()
        company_manager = self.injector.get(CompanyManager)
        worker = self.member_generator.create_member(name=worker_name)
        company_manager.add_worker_to_company(company, worker)
        response = self.client.get(URL)
        assert worker_name in response.text

    def test_post_yields_400_if_no_post_data_was_provided(self) -> None:
        self.login_company()
        response = self.client.post(URL)
        assert response.status_code == 400

    def test_post_yields_400_with_incorrect_uuid(self) -> None:
        self.login_company()
        response = self.client.post(URL, data={"worker_id": str(uuid4())})
        assert response.status_code == 400

    def test_post_yields_302_if_correct_data_was_provided(self) -> None:
        worker = self.member_generator.create_member()
        self.login_company()
        response = self.client.post(URL, data={"worker_id": str(worker)})
        assert response.status_code == 302
