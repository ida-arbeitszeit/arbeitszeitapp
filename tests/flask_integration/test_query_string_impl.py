from werkzeug.datastructures import MultiDict

from arbeitszeit_flask.flask_request import QueryStringImpl

from .base_test_case import FlaskTestCase


class QueryStringTests(FlaskTestCase):
    def test_can_get_values_passed_in(self) -> None:
        query_string = QueryStringImpl(MultiDict(mapping=dict(a="1")))
        assert query_string.get("a") == ["1"]

    def test_getting_values_that_are_not_in_arguments_yields_none(self) -> None:
        query_string = QueryStringImpl(MultiDict(mapping=dict(a="1")))
        assert query_string.get("b") == []
