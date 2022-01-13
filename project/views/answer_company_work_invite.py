from dataclasses import dataclass

from flask import Response
from injector import inject


@inject
@dataclass
class AnswerCompanyWorkInviteView:
    def respond_to_get(self, form, invite_id):
        return Response(status=200)
