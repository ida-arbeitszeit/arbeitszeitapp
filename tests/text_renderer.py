from typing import Any, Callable


class RenderMethod:
    def __set_name__(self, owner, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype=None) -> Callable[..., str]:
        def method(*args, **kwargs) -> str:
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
