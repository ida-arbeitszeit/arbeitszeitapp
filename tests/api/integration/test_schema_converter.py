from flask_restx import Model, Namespace, fields

from arbeitszeit_flask.api.schema_converter import (
    DifferentModelWithSameNameExists,
    json_schema_to_flaskx,
)
from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
)
from tests.api.integration.base_test_case import ApiTestCase


class SchemaConversionTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.namespace = Namespace(name="test_ns")
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

    def test_convert_to_integer_if_input_was_integer(self) -> None:
        model = JsonInteger()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.Integer)

    def test_convert_to_datetime_if_input_was_datetime(self) -> None:
        model = JsonDatetime()
        converted = self.convert(model, self.namespace)
        self.assertEqual(converted, fields.DateTime)

    def test_convert_to_model_if_input_was_object(self) -> None:
        obj = JsonObject(members={}, name="some_name")
        converted = self.convert(obj, self.namespace)
        self.assertIsInstance(converted, Model)
        self.assertEqual(converted, Model(name="some_name"))

    def test_convert_to_nested_model(self) -> None:
        obj = JsonObject(
            name="outer", members={"inner_obj": JsonObject(name="inner", members={})}
        )
        converted = self.convert(obj, self.namespace)
        assert isinstance(converted, Model)
        self.assertEqual(converted["inner_obj"], {})

    def test_convert_to_nested_model_with_value_of_string(self) -> None:
        obj = JsonObject(
            name="outer",
            members={
                "inner_obj": JsonObject(name="inner", members={"string": JsonString()})
            },
        )
        converted = self.convert(obj, self.namespace)
        assert isinstance(converted, Model)
        self.assertEqual(converted["inner_obj"]["string"], fields.String)

    def test_register_obj_on_namespace_with_correct_name(self) -> None:
        expected_name = "TestName"
        expected_model: dict = dict()
        obj = JsonObject(members=expected_model, name=expected_name)
        self.convert(obj, self.namespace)
        self.assertEqual(self.namespace.models[expected_name], expected_model)

    def test_register_obj_members_on_namespace_as_strings_if_string_was_given(
        self,
    ) -> None:
        obj = JsonObject(members={"item_name": JsonString()}, name="SchemaName")
        self.convert(obj, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        self.assertEqual(registered_model["item_name"], fields.String)

    def test_convert_object_members_to_list(
        self,
    ) -> None:
        obj = JsonObject(
            members={"item_name": JsonString(as_list=True)}, name="SchemaName"
        )
        self.convert(obj, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        self.assertIsInstance(registered_model["item_name"], fields.List)
        self.assertIsInstance(registered_model["item_name"].container, fields.String)

    def test_convert_nested_objects_to_list_of_nested_objects(
        self,
    ) -> None:
        model = JsonObject(
            members={
                "item_name": JsonObject(
                    name="some_name",
                    members={"some_string": JsonString()},
                    as_list=True,
                )
            },
            name="SchemaName",
        )
        self.convert(model, self.namespace)
        registered_model = self.namespace.models["SchemaName"]
        assert isinstance(registered_model["item_name"], fields.List)
        assert isinstance(registered_model["item_name"].container, fields.Nested)
        assert isinstance(
            registered_model["item_name"].container.model["some_string"], fields.String
        )

    def test_two_members_of_objects_are_registered_when_one_is_as_list(
        self,
    ) -> None:
        obj = JsonObject(
            members={
                "has_list_elements": JsonObject(
                    name="InnerModel",
                    as_list=True,
                    members=dict(one=JsonString(), two=JsonBoolean()),
                ),
                "has_no_list_elements": JsonDecimal(),
            },
            name="SchemaName",
            as_list=False,
        )
        self.convert(obj, self.namespace)
        registered_model = self.namespace.models["SchemaName"]

        self.assertEqual(len(registered_model), 2)
        self.assertTrue(registered_model["has_list_elements"])
        self.assertTrue(registered_model["has_no_list_elements"])

    def test_raise_exception_when_two_different_models_with_same_name_are_registered_on_same_namespace(
        self,
    ) -> None:
        model1 = JsonObject(members={"item_name": JsonString()}, name="SchemaName")
        model2 = JsonObject(members={"item_name2": JsonString()}, name="SchemaName")
        self.convert(model1, self.namespace)
        with self.assertRaises(DifferentModelWithSameNameExists):
            self.convert(model2, self.namespace)

    def test_no_error_is_raised_when_two_identical_models_with_same_name_are_registered_on_same_namespace(
        self,
    ) -> None:
        model1 = JsonObject(members={"item_name": JsonString()}, name="SchemaName")
        model2 = JsonObject(members={"item_name": JsonString()}, name="SchemaName")
        self.convert(model1, self.namespace)
        self.convert(model2, self.namespace)
