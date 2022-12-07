import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from arbeitszeit_web.json_handling import serialize_to_json
from tests.presenters.base_test_case import BaseTestCase


class JsonSerializerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.serialize = serialize_to_json

    def test_that_serialize_function_returns_empty_json_object_for_empty_dictionary(
        self,
    ):
        result = self.serialize(dict())
        self.assertEqual(result, "{}")

    def test_that_serialize_function_does_not_change_string(self):
        value = "10"
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], value)

    def test_that_serialize_function_does_not_change_integer(self):
        value = 10
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], value)

    def test_that_serialize_function_converts_uuid_to_string(self):
        value = uuid4()
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], str(value))

    def test_that_serialize_function_converts_decimal_to_string(self):
        value = Decimal("0.001")
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], "0.001")

    def test_that_serialize_function_converts_datetime_to_string_in_iso_8601_format_when_no_microseconds_are_given(
        self,
    ):
        value = datetime(year=2022, month=5, day=1, hour=15, minute=30, second=10)
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], "2022-05-01T15:30:10")

    def test_that_serialize_function_converts_datetime_to_string_in_iso_8601_format_when_microseconds_are_given(
        self,
    ):
        value = datetime(
            year=2022, month=5, day=1, hour=15, minute=30, second=10, microsecond=2222
        )
        result = self.serialize({"key": value})
        deserialized_result = self.deserialize(result)
        self.assertEqual(deserialized_result["key"], "2022-05-01T15:30:10.002222")

    def deserialize(self, json_string: str) -> Any:
        return json.loads(json_string)
