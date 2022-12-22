from flask_restx import fields

from arbeitszeit_web.api_presenters.interfaces import Decimal, Nested, String


class FieldTypes:
    def __init__(self) -> None:
        self.string: type[String] = fields.String
        self.decimal: type[Decimal] = fields.Arbitrary
        self.nested: type[Nested] = fields.Nested
