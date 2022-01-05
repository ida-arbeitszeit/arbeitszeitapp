from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, cast
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import AnswerCompanyWorkInviteRequest
from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInviteController
from arbeitszeit_web.malformed_input_data import MalformedInputData

from ..session import FakeSession


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.controller = AnswerCompanyWorkInviteController(self.session)

    def _get_request_form(self, invite_id: Optional[str] = None) -> FakeRequestForm:
        if invite_id is None:
            invite_id = str(uuid4())
        return FakeRequestForm(invite_id_field=invite_id)

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
        self.assertIsNone(self.controller.import_form_data(self._get_request_form()))


class LoggedInUsertests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.session.set_current_user_id(uuid4())

    def test_controller_returns_not_none_for_logged_in_user_when_importing_form_data(
        self,
    ) -> None:
        self.assertIsNotNone(self.controller.import_form_data(self._get_request_form()))

    def test_controller_returns_malformed_input_data_with_invalid_uuid_as_invite_id(
        self,
    ) -> None:
        self.assertIsInstance(
            self.controller.import_form_data(self._get_request_form(invite_id="")),
            MalformedInputData,
        )

    def test_request_contains_correct_uuid_from_form_data(
        self,
    ) -> None:
        expected_uuid = uuid4()
        request = self.controller.import_form_data(
            self._get_request_form(invite_id=str(expected_uuid))
        )
        self.assertSuccess(request, lambda r: r.invite_id == expected_uuid)


@dataclass
class FakeRequestForm:
    invite_id_field: str

    def get_invite_id_field(self) -> str:
        return self.invite_id_field
