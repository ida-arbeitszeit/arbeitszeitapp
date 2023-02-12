from arbeitszeit_flask.flask_request import QueryStringImpl

from .flask import FlaskTestCase


class QueryStringTests(FlaskTestCase):
    def test_can_get_values_passed_in(self) -> None:
        query_string = QueryStringImpl(dict(a="1"))
        self.assertEqual(query_string.get("a"), "1")

    def test_getting_values_that_are_not_in_arguments_yields_none(self) -> None:
        query_string = QueryStringImpl(dict(a="1"))
        self.assertIsNone(query_string.get("b"))
