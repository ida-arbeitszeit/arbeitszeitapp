from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Company, Member, Message
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    MessageRepository,
)
from arbeitszeit.user_action import UserAction


@inject
@dataclass
class ReadMessage:
    member_repository: MemberRepository
    message_repository: MessageRepository
    company_repository: CompanyRepository

    def __call__(self, request: ReadMessageRequest) -> ReadMessageResponse:
        try:
            message = self._validate_request(request)
        except ReadMessageFailure as failure:
            return failure
        self.message_repository.mark_as_read(message)
        return ReadMessageSuccess(
            message_title=message.title,
            message_content=message.content,
            sender_remarks=message.sender_remarks,
            user_action=message.user_action,
        )

    def _validate_request(self, request: ReadMessageRequest) -> Message:
        reader = self._get_reader(request)
        if reader is None:
            raise ReadMessageFailure()
        message = self.message_repository.get_by_id(request.message_id)
        if message is None:
            raise ReadMessageFailure()
        if message.addressee != reader:
            raise ReadMessageFailure()
        return message

    def _get_reader(self, request: ReadMessageRequest) -> Union[None, Member, Company]:
        return self.member_repository.get_by_id(
            request.reader_id
        ) or self.company_repository.get_by_id(request.reader_id)


ReadMessageResponse = Union["ReadMessageFailure", "ReadMessageSuccess"]


class ReadMessageFailure(Exception):
    pass


@dataclass
class ReadMessageSuccess:
    message_title: str
    message_content: str
    sender_remarks: Optional[str]
    user_action: Optional[UserAction]


@dataclass
class ReadMessageRequest:
    reader_id: UUID
    message_id: UUID
