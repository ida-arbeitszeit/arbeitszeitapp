from unittest import TestCase

from parameterized import parameterized

from arbeitszeit_flask.config.checks import (
    ConfigOptionMissing,
    ConfigOptionTypeInvalid,
    ConfigValidator,
)
from arbeitszeit_flask.config.options import ConfigOption


class ConfigValidatorTests(TestCase):
    def setUp(self):
        super().setUp()

    def test_validator_raises_exception_if_expected_option_is_missing(self) -> None:
        config = {}
        EXPECTED_OPTION_NAME = "SERVER_NAME"
        config["OTHER_OPTION"] = "some option"
        expected_options = [self.create_option(EXPECTED_OPTION_NAME, str)]
        with self.assertRaises(ConfigOptionMissing):
            self.validate(config, expected_options)

    @parameterized.expand(
        [
            ("not-a-boolean",),
            ("123,5",),
            ("123.5",),
            123.5,
            ("",),
        ]
    )
    def test_validator_raises_exception_if_expected_option_is_not_integer(
        self, value: str | float
    ) -> None:
        config = {}
        EXPECTED_OPTION_NAME = "OPTION"
        config[EXPECTED_OPTION_NAME] = value
        expected_options = [self.create_option(EXPECTED_OPTION_NAME, int)]
        with self.assertRaises(ConfigOptionTypeInvalid):
            self.validate(config, expected_options)

    def test_that_config_passes_validation_if_it_is_string(self) -> None:
        config = {}
        EXPECTED_OPTION_NAME = "SERVER_NAME"
        config[EXPECTED_OPTION_NAME] = "some.server.name"
        expected_options = [self.create_option(EXPECTED_OPTION_NAME, str)]
        self.validate(config, expected_options)

    @parameterized.expand(
        [
            ("8080",),
            (8080,),
            ("-12",),
            (-12,),
        ]
    )
    def test_that_config_passes_validation_if_option_is_integer(
        self, value: str | int
    ) -> None:
        config = {}
        EXPECTED_OPTION_NAME = "SERVER_PORT"
        config[EXPECTED_OPTION_NAME] = value
        expected_options = [self.create_option(EXPECTED_OPTION_NAME, int)]
        self.validate(config, expected_options)

    @parameterized.expand(
        [
            ("true",),
            ("false",),
            ("True",),
            ("False",),
            ("1",),
            ("0",),
            (1,),
            (0,),
            (True,),
            (False,),
        ]
    )
    def test_that_config_passes_validation_if_option_can_be_converted_to_boolean(
        self, value: str | int | bool
    ) -> None:
        config = {}
        EXPECTED_OPTION_NAME = "SERVER_NAME"
        config[EXPECTED_OPTION_NAME] = value
        expected_options = [self.create_option(EXPECTED_OPTION_NAME, bool)]
        self.validate(config, expected_options)

    def create_option(self, name: str, type_: type = str) -> ConfigOption:
        return ConfigOption(name=name, converts_to_types=(type_,))

    def validate(self, config: dict, expected_options: list[ConfigOption]) -> None:
        verifyer = ConfigValidator(
            config=config, expected_options=set(expected_options)
        )
        verifyer.validate_options()
        verifyer.validate_option_types()
