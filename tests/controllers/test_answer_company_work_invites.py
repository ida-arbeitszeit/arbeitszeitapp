from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, cast
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import AnswerCompanyWorkInviteRequest
from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInviteController

from ..session import FakeSession


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.controller = AnswerCompanyWorkInviteController(self.session)

    def _get_request_form(self, is_accepted: bool = True) -> FakeRequestForm:
        return FakeRequestForm(is_accepted=is_accepted)

    def assertSuccess(
        self,
        candidate: Any,
        condition: Callable[[AnswerCompanyWorkInviteRequest], bool],
    ) -> None:
        self.assertIsInstance(candidate, AnswerCompanyWorkInviteRequest)
        self.assertTrue(condition(cast(AnswerCompanyWorkInviteRequest, candidate)))


class AnonymousUserTests(BaseTestCase):
    def test_that_controller_returns_none_when_importing_form_data_from_anonymous_user(
        self,
    ) -> None:
        self.assertIsNone(
            self.controller.import_form_data(
                self._get_request_form(), invite_id=uuid4()
            )
        )


class LoggedInUsertests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.requesting_user = uuid4()
        self.session.set_current_user_id(self.requesting_user)

    def test_controller_returns_not_none_for_logged_in_user_when_importing_form_data(
        self,
    ) -> None:
        self.assertIsNotNone(
            self.controller.import_form_data(
                self._get_request_form(), invite_id=uuid4()
            )
        )

    def test_request_contains_correct_uuid_from_form_data(
        self,
    ) -> None:
        expected_uuid = uuid4()
        request = self.controller.import_form_data(
            self._get_request_form(),
            invite_id=expected_uuid,
        )
        self.assertSuccess(request, lambda r: r.invite_id == expected_uuid)

    def test_when_form_rejects_invite_then_render_request_that_rejects_invite(self):
        request = self.controller.import_form_data(
            self._get_request_form(is_accepted=False),
            invite_id=uuid4(),
        )
        self.assertSuccess(request, lambda r: not r.is_accepted)

    def test_when_form_accepts_invite_then_render_request_that_accepts_invite(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            self._get_request_form(is_accepted=True),
            invite_id=uuid4(),
        )
        self.assertSuccess(request, lambda r: r.is_accepted)

    def test_render_user_id_of_requesting_user_in_resulting_response(self) -> None:
        request = self.controller.import_form_data(
            self._get_request_form(), invite_id=uuid4()
        )
        self.assertSuccess(request, lambda r: r.user == self.requesting_user)


@dataclass
class FakeRequestForm:
    is_accepted: bool

    def get_is_accepted_field(self) -> bool:
        return self.is_accepted
