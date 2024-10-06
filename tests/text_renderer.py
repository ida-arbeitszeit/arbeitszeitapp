from typing import Any, Callable, Optional


class RenderMethod:
    def __set_name__(self, owner: Any, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype: Optional[Any] = None) -> Callable[..., str]:
        def method(*args: Any, **kwargs: Any) -> str:
            sorted_args = [str(argument) for argument in args]
            sorted_args.sort()
            sorted_kwargs = [f"{key}: {value}" for key, value in kwargs.items()]
            sorted_kwargs.sort()
            return f"placeholder text for {self._attribute_name}, context: args={args}, kwargs={kwargs}"

        return method


class TextRendererImpl:
    render_member_registration_message = RenderMethod()
    render_company_registration_message = RenderMethod()
    render_accountant_notification_about_new_plan = RenderMethod()
    render_member_notfication_about_work_invitation = RenderMethod()
    render_email_change_warning = RenderMethod()
    render_email_change_notification = RenderMethod()
    render_company_notification_about_rejected_plan = RenderMethod()
