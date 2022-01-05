from arbeitszeit.use_cases import RegisterMemberRequest


class RegisterMemberController:
    def create_request(
        self,
        email: str,
        name: str,
        password: str,
        email_subject: str,
        email_html: str,
        email_sender: str,
    ) -> RegisterMemberRequest:
        return RegisterMemberRequest(
            email=email,
            name=name,
            password=password,
            email_subject=email_subject,
            email_html=email_html,
            email_sender=email_sender,
        )
