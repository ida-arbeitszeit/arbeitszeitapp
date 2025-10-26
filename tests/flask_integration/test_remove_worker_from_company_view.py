from uuid import uuid4

from tests.flask_integration.base_test_case import ViewTestCase


class TestGet(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/remove_worker_from_company"

    def test_logged_in_company_gets_200(self) -> None:
        worker = self.member_generator.create_member()
        password = f"{uuid4()}"
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            workers=[worker], password=password, email=email
        )
        self.login_company(password=password, email=email)
        response = self.client.get(self.url)
        assert response.status_code == 200


class TestPost(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/remove_worker_from_company"

    def test_redirects_on_success(self) -> None:
        worker = self.member_generator.create_member()
        password = f"{uuid4()}"
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            workers=[worker], password=password, email=email
        )
        self.login_company(password=password, email=email)
        response = self.client.post(self.url, data=dict(worker=f"{worker}"))
        assert response.status_code == 302

    def test_one_email_is_sent_on_success(self) -> None:
        worker = self.member_generator.create_member()
        password = f"{uuid4()}"
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            workers=[worker], password=password, email=email
        )
        self.login_company(password=password, email=email)
        with self.email_service().record_messages() as outbox:
            response = self.client.post(self.url, data=dict(worker=f"{worker}"))
            assert response.status_code == 302
            assert len(outbox) == 1

    def test_no_email_is_sent_on_failure(self) -> None:
        worker = self.member_generator.create_member()
        password = f"{uuid4()}"
        email = self.email_generator.get_random_email()
        self.company_generator.create_company(
            workers=[worker], password=password, email=email
        )
        self.login_company(password=password, email=email)
        with self.email_service().record_messages() as outbox:
            assert len(outbox) == 0
            response = self.client.post(self.url, data=dict(worker="no-uuid"))
            assert response.status_code >= 400
            assert len(outbox) == 0
