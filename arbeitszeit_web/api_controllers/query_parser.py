from arbeitszeit_web.api_controllers.errors import (
    NegativeNumberError,
    NotAnIntegerError,
)


def string_to_non_negative_integer(string: str) -> int:
    try:
        integer = int(string)
    except ValueError:
        raise NotAnIntegerError()
    else:
        if integer < 0:
            raise NegativeNumberError()
    return integer
