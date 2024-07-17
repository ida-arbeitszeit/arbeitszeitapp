from ._axes import Axes as Axes

Subplot = Axes

class _SubplotBaseMeta(type):
    def __instancecheck__(self, obj): ...

class SubplotBase(metaclass=_SubplotBaseMeta): ...

def subplot_class_factory(cls): ...
