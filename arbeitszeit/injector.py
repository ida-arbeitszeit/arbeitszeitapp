from __future__ import annotations

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    get_type_hints,
)

S = TypeVar("S")
T = TypeVar("T")
T_cov = TypeVar("T_cov", covariant=True)
CallableT = TypeVar("CallableT", bound=Callable)
TypeT = TypeVar("TypeT", bound=Type)
ProviderFunction = Callable[[Type[T]], "Provider[T]"]


class Injector:
    def __init__(self, modules: List[Module]) -> None:
        class _RecursionModule(Module):
            def configure(module_self, binder: Binder) -> None:
                super().configure(binder)
                binder[Injector] = InstanceProvider(self)

        recursion_module = _RecursionModule()

        self.binder: Binder = Binder(Injector.default_provider)
        recursion_module.configure(self.binder)
        for module in modules:
            module.configure(self.binder)

    @staticmethod
    def default_provider(cls: Type[T]) -> ClassProvider[T]:
        return ClassProvider(cls)

    def get(self, cls: Type[T]) -> T:
        provider = self.binder.get(cls)
        return provider.provide(self.binder)

    def call_with_injection(
        self,
        f: Callable[..., T],
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> T:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        signature = inspect.signature(f)
        bound_arguments = signature.bind_partial(*args)
        dependencies = dict()
        for key, value in get_type_hints(f).items():
            if (
                key != "return"
                and key not in bound_arguments.arguments
                and key not in kwargs
            ):
                dependencies[key] = self.get(value)
        dependencies.update(kwargs)
        return f(*bound_arguments.arguments.values(), **dependencies)

    def create_object(self, cls: Type[T], additional_kwargs: Dict[str, Any]) -> T:
        return self.call_with_injection(cls, kwargs=additional_kwargs)


class Binder:
    def __init__(self, default: ProviderFunction) -> None:
        self._default = default
        self._bindings: Dict[Type, Provider] = dict()
        self._instances: Dict[Type, Any] = dict()

    def __getitem__(self, key: Type[T]) -> Provider[T]:
        return self._bindings[key]

    def __setitem__(self, key: Type[T], value: Provider[T]) -> None:
        self._bindings[key] = value

    def __contains__(self, key: Type[T]) -> bool:
        return key in self._bindings

    def bind(self, cls: Type[T], to: Provider[T]) -> None:
        self._bindings[cls] = to

    def get(self, cls: Type[T]) -> Provider[T]:
        if cls not in self:
            return self._default(cls)
        else:
            return self[cls]


class Provider(Protocol, Generic[T_cov]):
    def provide(self, binder: Binder) -> T_cov: ...


class AliasProvider(Generic[T]):
    """This provider provides instances by simply refering to another
    class.  This can be useful when specifying the concret
    implementation of an abstract base class (ABC) or a Protocol.
    """

    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    def provide(self, binder: Binder) -> T:
        provider = binder.get(self.cls)
        return provider.provide(binder)


class InstanceProvider(Provider[T]):
    """Provide an instance of of a class by specifying the concrete
    instance in the provider.
    """

    def __init__(self, instance: T) -> None:
        self.instance = instance

    def provide(self, binder: Binder) -> T:
        return self.instance


class ClassProvider(Provider[T]):
    """Provide an instance of a type by calling its constructor
    (__init__ method) and providing its arguments from dependency
    injection.

    This provider usually doen't need to be specified directly since
    it is assumed to be the default in case no other provider was
    specified.
    """

    def __init__(self, cls: Type[T]) -> None:
        self.cls = cls

    def provide(self, binder: Binder) -> T:
        if self.is_singleton:
            instance = binder._instances.get(self.cls)
            if instance is not None:
                return instance
        args = get_type_hints(self.cls.__init__)
        kwargs = dict()
        for name, annotation in args.items():
            if name == "return":
                continue
            kwargs[name] = binder.get(annotation).provide(binder)
        try:
            instance = self.cls(**kwargs)
        except TypeError as e:
            raise TypeError(f"Could not create instance of class {self.cls}") from e
        if self.is_singleton:
            binder._instances[self.cls] = instance
        return instance

    @property
    def is_singleton(self) -> bool:
        return getattr(self.cls, "_injection_singleton", False)


class CallableProvider(Provider[T]):
    """Provide an instance by calling a function.  The arguments to
    the function will be provide by dependency injection.
    """

    def __init__(self, f: Callable[..., T], is_singleton: bool = False) -> None:
        self.f = f
        self._is_singleton = is_singleton

    def provide(self, binder: Binder) -> T:
        if self._is_singleton:
            instance = binder._instances.get(self.return_type)
            if instance:
                return instance
        args = get_type_hints(self.f)
        kwargs = dict()
        for name, annotation in args.items():
            if name == "return":
                continue
            kwargs[name] = binder.get(annotation).provide(binder)
        instance = self.f(**kwargs)
        if self._is_singleton:
            binder._instances[self.return_type] = instance
        return instance

    @property
    def return_type(self) -> Type:
        hints = get_type_hints(self.f)
        return hints["return"]


class Module:
    def configure(self, binder: Binder) -> None:
        pass


def singleton(cls: TypeT) -> TypeT:
    cls._injection_singleton = True
    return cls
