from typing import Dict

from flask_restx import fields

from arbeitszeit_flask.api.schema_converter import (
    ModelWithSameNameExists,
    json_schema_to_flaskx,
)
from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonDict,
    JsonString,
)
from tests.api.implementations import NamespaceImpl
from tests.api.integration.base_test_case import ApiTestCase


class SchemaConversionTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.namespace = NamespaceImpl(
            name="test_ns", description="Test related endpoints"
        )
        self.convert = json_schema_to_flaskx

    def test_convert_to_string_if_input_was_string(self) -> None:
        model = JsonString()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.String)

    def test_convert_to_arbitrary_float_if_input_was_decimal(self) -> None:
        model = JsonDecimal()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.Arbitrary)

    def test_convert_to_boolean_if_input_was_boolean(self) -> None:
        model = JsonBoolean()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.Boolean)

    def test_convert_to_datetime_if_input_was_datetime(self) -> None:
        model = JsonDatetime()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.DateTime)

    def test_convert_to_dict_if_input_was_dict(self) -> None:
        model = JsonDict(members={})
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, {})

    def test_convert_to_nested_dict(self) -> None:
        model = JsonDict(members={"inner_dict": JsonDict(members={})})
        converted = self.convert(model, self.namespace)
        assert isinstance(converted, Dict)
        self.assertEqual(converted["inner_dict"], {})

    def test_convert_to_nested_dict_with_value_string(self) -> None:
        model = JsonDict(
            members={"inner_dict": JsonDict(members={"string": JsonString()})}
        )
        converted = self.convert(model, self.namespace)
        assert isinstance(converted, Dict)
        self.assertEqual(converted["inner_dict"]["string"], fields.String)

    def test_do_not_register_dict_on_namespace_if_no_name_was_provided(self) -> None:
        model = JsonDict(members={}, schema_name=None)
        self.convert(model, self.namespace)
        self.assertFalse(self.namespace.models)

    def test_register_dict_on_namespace_if_name_was_provided(self) -> None:
        model = JsonDict(members={}, schema_name="TestName")
        self.convert(model, self.namespace)
        self.assertTrue(self.namespace.models)

    def test_register_dict_members_on_namespace_as_strings_if_string_was_given(
        self,
    ) -> None:
        model = JsonDict(members={"item_name": JsonString()}, schema_name="SchemaName")
        self.convert(model, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        self.assertEqual(registered_model["item_name"], fields.String)

    def test_register_dict_members_on_namespace_as_nested_if_as_list_was_given(
        self,
    ) -> None:
        model = JsonDict(
            members={"item_name": JsonString(as_list=True)}, schema_name="SchemaName"
        )
        self.convert(model, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        self.assertIsInstance(registered_model["item_name"], fields.Nested)
        self.assertTrue(registered_model["item_name"].as_list)

    def test_register_dict_members_on_namespace_as_nested_string_if_as_list_was_given(
        self,
    ) -> None:
        model = JsonDict(
            members={"item_name": JsonString(as_list=True)}, schema_name="SchemaName"
        )
        self.convert(model, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        assert isinstance(registered_model["item_name"], fields.Nested)
        self.assertEqual(registered_model["item_name"].model, fields.String)

    def test_two_members_of_dict_are_registered_when_one_is_as_list(
        self,
    ) -> None:
        model = JsonDict(
            members={
                "has_list_elements": JsonDict(
                    schema_name="InnerModel",
                    as_list=True,
                    members=dict(one=JsonString(), two=JsonBoolean()),
                ),
                "has_no_list_elements": JsonDecimal(),
            },
            schema_name="SchemaName",
            as_list=False,
        )
        self.convert(model, self.namespace)
        registered_model = self.namespace.models["SchemaName"]

        self.assertEqual(len(registered_model), 2)
        self.assertTrue(registered_model["has_list_elements"])
        self.assertTrue(registered_model["has_no_list_elements"])

    def test_raise_exception_when_two_models_with_same_name_are_registered_on_same_namespace(
        self,
    ) -> None:
        model1 = JsonDict(members={"item_name": JsonString()}, schema_name="SchemaName")
        model2 = JsonDict(
            members={"item_name2": JsonString()}, schema_name="SchemaName"
        )
        self.convert(model1, self.namespace)
        with self.assertRaises(ModelWithSameNameExists):
            self.convert(model2, self.namespace)
