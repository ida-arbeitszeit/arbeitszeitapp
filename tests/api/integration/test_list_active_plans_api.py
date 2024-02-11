from parameterized import parameterized

from tests.api.integration.base_test_case import ApiTestCase


class AnonymousUserTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"

    def test_anonymous_user_gets_status_code_401_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_gets_corrrect_error_message_on_get_request(self):
        expected_message = "You have to authenticate before using this service."
        response = self.client.get(self.url)
        self.assertEqual(response.json["message"], expected_message)

    def test_anonymous_user_gets_mimetype_application_json_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")


class AuthenticatedCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"
        self.login_company()

    def test_company_gets_status_code_200_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 200)


class AuthenticatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"
        self.login_member()

    def test_member_gets_status_code_200_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            (0,),
            (75,),
        ]
    )
    def test_member_gets_status_code_200_when_query_parameter_offset_is_a_positive_number(
        self,
        offset: int,
    ):
        response = self.client.get(self.url, query_string={"offset": offset})
        self.assertEqual(response.status_code, 200)

    def test_member_gets_status_code_400_when_query_parameter_offset_is_a_negative_number(
        self,
    ):
        response = self.client.get(self.url, query_string={"offset": -1})
        self.assertEqual(response.status_code, 400)

    @parameterized.expand(
        [
            (0,),
            (75,),
        ]
    )
    def test_member_gets_status_code_200_when_query_parameter_limit_is_a_positive_number(
        self,
        offset: int,
    ):
        response = self.client.get(self.url, query_string={"limit": offset})
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            (3, 7),
            (100, 5),
        ]
    )
    def test_member_gets_status_code_200_with_offset_and_limit_set_to_positive_numbers(
        self,
        offset: int,
        limit: int,
    ):
        response = self.client.get(
            self.url, query_string={"offset": offset, "limit": limit}
        )
        self.assertEqual(response.status_code, 200)

    def test_member_gets_status_code_400_when_letters_are_in_offset_param(
        self,
    ):
        response = self.client.get(self.url, query_string={"offset": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_member_gets_status_code_405_on_post_request(self):
        response = self.client.post(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)
