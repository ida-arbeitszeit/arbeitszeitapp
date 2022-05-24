from flask import Response

from .blueprint import AccountantRoute


@AccountantRoute("/accountant/dashboard")
def dashboard():
    return Response("", status=200)
