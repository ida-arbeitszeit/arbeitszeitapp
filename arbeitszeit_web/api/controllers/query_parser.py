from arbeitszeit_web.api.presenters.response_errors import BadRequest


def string_to_non_negative_integer(string: str) -> int:
    try:
        integer = int(string)
    except ValueError:
        raise BadRequest(f"Input must be an integer, not {string}.")
    else:
        if integer < 0:
            raise BadRequest(f"Input must be greater or equal zero, not {string}.")
    return integer
