from typing import Any, overload

import numpy

def delaunay(
    x: numpy.ndarray[numpy.float64], y: numpy.ndarray[numpy.float64], verbose: int
) -> tuple: ...
@overload
def version() -> str: ...
@overload
def version() -> Any: ...
