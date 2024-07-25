import numpy

TK_PHOTO_COMPOSITE_OVERLAY: int
TK_PHOTO_COMPOSITE_SET: int

def blit(
    interp: object,
    photo_name: str,
    data: numpy.ndarray[numpy.uint8],
    comp_rule: int,
    offset: tuple[int, int, int, int],
    bbox: tuple[int, int, int, int],
) -> None: ...
def enable_dpi_awareness(frame_handle: object, interp: object) -> object: ...
