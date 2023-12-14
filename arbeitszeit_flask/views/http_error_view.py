from flask import Response, render_template


def http_error(code: int, reason: str) -> Response:
    return Response(
        render_template(
            "user/http_error.html",
            view_model=dict(code=code, reason=reason),
        ),
        status=code,
    )


def http_404() -> Response:
    return http_error(code=404, reason="NOT FOUND")


def http_403() -> Response:
    return http_error(code=403, reason="FORBIDDEN")


def http_409() -> Response:
    return http_error(code=409, reason="CONFLICT")


def http_501() -> Response:
    return http_error(code=501, reason="NOT IMPLEMENTED")
