from _typeshed import Incomplete

from .geo import AitoffAxes as AitoffAxes
from .geo import HammerAxes as HammerAxes
from .geo import LambertAxes as LambertAxes
from .geo import MollweideAxes as MollweideAxes
from .polar import PolarAxes as PolarAxes

class ProjectionRegistry:
    def __init__(self) -> None: ...
    def register(self, *projections) -> None: ...
    def get_projection_class(self, name): ...
    def get_projection_names(self): ...

projection_registry: Incomplete

def register_projection(cls) -> None: ...
def get_projection_class(projection: Incomplete | None = None): ...

get_projection_names: Incomplete
