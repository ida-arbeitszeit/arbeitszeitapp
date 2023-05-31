from typing import Optional, Type, Union

from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_web.api_controllers.expected_input import ExpectedInput, InputLocation
from tests.api.integration.base_test_case import ApiTestCase


class TestInputConverter(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.convert = generate_input_documentation

    def test_converter_returns_empty_inputs_into_request_parser_with_no_argument(self):
        parser = self.convert(expected_inputs=[])
        assert parser
        assert not parser.args

    def test_converter_returns_one_input_into_request_parser_with_one_argument(self):
        parser = self.convert(expected_inputs=[self.create_expected_input()])
        assert parser
        assert len(parser.args) == 1

    def test_converter_returns_two_inputs_into_request_parser_with_two_arguments(self):
        parser = self.convert(
            expected_inputs=[self.create_expected_input(), self.create_expected_input()]
        )
        assert parser
        assert len(parser.args) == 2

    def test_converter_returns_one_input_into_request_parser_with_one_argument_with_correct_params(
        self,
    ):
        expected_name = "example"
        expected_type = str
        expected_description = "test description"
        expected_default = "default"
        input = self.create_expected_input(
            name=expected_name,
            type=expected_type,
            description=expected_description,
            default=expected_default,
        )
        parser = self.convert(expected_inputs=[input])
        argument = parser.args[0]
        assert argument.name == expected_name
        assert argument.type == expected_type
        assert argument.help == expected_description
        assert argument.default == expected_default

    def test_query_input_location_gets_converted_to_correct_string(
        self,
    ):
        input = self.create_expected_input(location=InputLocation.query)
        parser = self.convert(expected_inputs=[input])
        argument = parser.args[0]
        self.assertEqual(argument.location, "query")

    def test_form_input_location_gets_converted_to_correct_string(
        self,
    ):
        input = self.create_expected_input(location=InputLocation.form)
        parser = self.convert(expected_inputs=[input])
        argument = parser.args[0]
        self.assertEqual(argument.location, "form")

    def test_path_input_location_gets_converted_to_correct_string(
        self,
    ):
        input = self.create_expected_input(location=InputLocation.path)
        parser = self.convert(expected_inputs=[input])
        argument = parser.args[0]
        self.assertEqual(argument.location, "path")

    def test_converter_returns_two_inputs_into_request_parser_with_two_different_arguments(
        self,
    ):
        parser = self.convert(
            expected_inputs=[
                self.create_expected_input(name="name1"),
                self.create_expected_input(name="name2"),
            ]
        )
        argument1 = parser.args[0]
        argument2 = parser.args[1]
        assert argument1.name != argument2.name

    def create_expected_input(
        self,
        name: Optional[str] = None,
        type: Optional[Type] = None,
        description: Optional[str] = None,
        default: Union[None, str, int, bool] = None,
        required: Optional[bool] = None,
        location: Optional[InputLocation] = None,
    ) -> ExpectedInput:
        if name is None:
            name = "example"
        if type is None:
            type = str
        if description is None:
            description = "test description"
        if default is None:
            default = "default"
        if required is None:
            required = False
        if location is None:
            location = InputLocation.query
        return ExpectedInput(
            name=name,
            type=type,
            description=description,
            location=location,
            default=default,
            required=required,
        )
