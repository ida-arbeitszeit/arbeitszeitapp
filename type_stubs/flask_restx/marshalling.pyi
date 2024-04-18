from _typeshed import Incomplete

from .mask import Mask as Mask
from .utils import unpack as unpack

def make(cls): ...
def marshal(
    data,
    fields,
    envelope: Incomplete | None = None,
    skip_none: bool = False,
    mask: Incomplete | None = None,
    ordered: bool = False,
): ...

class marshal_with:
    fields: Incomplete
    envelope: Incomplete
    skip_none: Incomplete
    ordered: Incomplete
    mask: Incomplete
    def __init__(
        self,
        fields,
        envelope: Incomplete | None = None,
        skip_none: bool = False,
        mask: Incomplete | None = None,
        ordered: bool = False,
    ) -> None: ...
    def __call__(self, f): ...

class marshal_with_field:
    field: Incomplete
    def __init__(self, field) -> None: ...
    def __call__(self, f): ...
