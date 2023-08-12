from .geo import AitoffAxes as AitoffAxes, HammerAxes as HammerAxes, LambertAxes as LambertAxes, MollweideAxes as MollweideAxes
from .polar import PolarAxes as PolarAxes
from _typeshed import Incomplete

class ProjectionRegistry:
    def __init__(self) -> None: ...
    def register(self, *projections) -> None: ...
    def get_projection_class(self, name): ...
    def get_projection_names(self): ...

projection_registry: Incomplete

def register_projection(cls) -> None: ...
def get_projection_class(projection: Incomplete | None = ...): ...

get_projection_names: Incomplete
