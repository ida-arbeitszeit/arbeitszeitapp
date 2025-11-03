from dataclasses import dataclass

from arbeitszeit.interactors import request_email_address_change as interactor
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_web.forms import RequestEmailAddressChangeForm
from arbeitszeit_web.session import Session, UserRole


@dataclass
class RequestEmailAddressChangeController:
    database: DatabaseGateway
    session: Session

    def process_email_address_change_request(
        self, form: RequestEmailAddressChangeForm
    ) -> interactor.Request:
        current_user_id = self.session.get_current_user()
        assert current_user_id
        if self.session.get_user_role() == UserRole.member:
            email_address = (
                self.database.get_email_addresses()
                .that_belong_to_member(current_user_id)
                .first()
            )
        elif self.session.get_user_role() == UserRole.company:
            email_address = (
                self.database.get_email_addresses()
                .that_belong_to_company(current_user_id)
                .first()
            )
        elif self.session.get_user_role() == UserRole.accountant:
            query = (
                self.database.get_accountants()
                .with_id(current_user_id)
                .joined_with_email_address()
                .first()
            )
            assert query
            email_address = query[1]
        assert email_address
        return interactor.Request(
            current_email_address=email_address.address,
            new_email_address=form.new_email_field.get_value(),
            current_password=form.current_password_field.get_value(),
        )
