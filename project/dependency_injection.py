from functools import wraps

from flask_sqlalchemy import SQLAlchemy
from injector import (
    Binder,
    CallableProvider,
    ClassProvider,
    Injector,
    InstanceProvider,
    inject,
)

from arbeitszeit import entities
from arbeitszeit import repositories as interfaces
from arbeitszeit.datetime_service import DatetimeService
from project.database import get_social_accounting
from project.database.repositories import (
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    CooperationRepository,
    MemberRepository,
    MessageRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    WorkerInviteRepository,
)
from project.datetime import RealtimeDatetimeService
from project.extensions import db


def configure_injector(binder: Binder) -> None:
    binder.bind(
        interfaces.TransactionRepository,  # type: ignore
        to=ClassProvider(TransactionRepository),
    )
    binder.bind(
        interfaces.CompanyWorkerRepository,  # type: ignore
        to=ClassProvider(CompanyWorkerRepository),
    )
    binder.bind(
        interfaces.PurchaseRepository,  # type: ignore
        to=ClassProvider(PurchaseRepository),
    )
    binder.bind(
        entities.SocialAccounting,
        to=CallableProvider(get_social_accounting),
    )
    binder.bind(
        interfaces.AccountRepository,  # type: ignore
        to=ClassProvider(AccountRepository),
    )
    binder.bind(
        interfaces.MemberRepository,  # type: ignore
        to=ClassProvider(MemberRepository),
    )
    binder.bind(
        interfaces.CompanyRepository,  # type: ignore
        to=ClassProvider(CompanyRepository),
    )
    binder.bind(
        interfaces.PurchaseRepository,  # type: ignore
        to=ClassProvider(PurchaseRepository),
    )
    binder.bind(
        interfaces.PlanRepository,  # type: ignore
        to=ClassProvider(PlanRepository),
    )
    binder.bind(
        interfaces.AccountOwnerRepository,  # type: ignore
        to=ClassProvider(AccountOwnerRepository),
    )
    binder.bind(
        interfaces.PlanDraftRepository,  # type: ignore
        to=ClassProvider(PlanDraftRepository),
    )
    binder.bind(
        DatetimeService,  # type: ignore
        to=ClassProvider(RealtimeDatetimeService),
    )
    binder.bind(
        interfaces.WorkerInviteRepository,  # type: ignore
        to=ClassProvider(WorkerInviteRepository),
    )
    binder.bind(
        SQLAlchemy,
        to=InstanceProvider(db),
    )
    binder.bind(
        interfaces.MessageRepository,  # type: ignore
        to=ClassProvider(MessageRepository),
    )
    binder.bind(
        interfaces.CooperationRepository,  # type: ignore
        to=ClassProvider(CooperationRepository),
    )


_injector = Injector(configure_injector)


def with_injection(original_function):
    """When you wrap a function, make sure that the parameters to be
    injected come after the the parameters that the caller should
    provide.
    """

    @wraps(original_function)
    def wrapped_function(*args, **kwargs):
        return _injector.call_with_injection(
            inject(original_function), args=args, kwargs=kwargs
        )

    return wrapped_function
