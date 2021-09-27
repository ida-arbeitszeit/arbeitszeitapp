from uuid import uuid4

from tests.data_generators import MemberGenerator

from .dependency_injection import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        email = "member@cp.org"
        password = "12345"
        member_generator = self.injector.get(MemberGenerator)
        member = member_generator.create_member(
            email=email,
            password=password,
        )
        self.client.post(
            "/member/login",
            data=dict(
                email=member.email,
                password=password,
            ),
            follow_redirects=True,
        )

    def test_get_returns_200_status(self) -> None:
        response = self.client.get("/member/pay_consumer_product")
        self.assertEqual(response.status_code, 200)

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post("/member/pay_consumer_product")
        self.assertEqual(response.status_code, 400)

    def test_posting_with_invalid_form_data_results_in_400(self) -> None:
        response = self.client.post(
            "/member/pay_consumer_product",
            data=dict(
                plan_id=uuid4(),
                amount="abc",
            ),
        )
        self.assertEqual(response.status_code, 400)
