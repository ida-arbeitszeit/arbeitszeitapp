from typing import Any, Generic, Type, TypeVar

T = TypeVar("T")


# This class is a descriptor. Check
# https://docs.python.org/3/howto/descriptor.html for more information
# on descriptors.
class _lazy_property(Generic[T]):
    def __init__(self, cls: Type[T]):
        """
        Implement a lazy property for test base classes.
        If the implementor asks for this attribute then it is generated on
        demand and cached.
        """
        self.cls = cls

    def __set_name__(self, owner, name: str) -> None:
        self._attribute_name = name

    def __get__(self, obj: Any, objtype=None) -> T:
        cache = obj._lazy_property_cache
        instance = cache.get(self._attribute_name)
        if instance is None:
            instance = obj.injector.get(self.cls)
            cache[self._attribute_name] = instance
        return instance

    def __set__(self, obj: Any, value: T) -> None:
        raise Exception("This attribute is read-only")
