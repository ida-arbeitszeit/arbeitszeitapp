from _typeshed import Incomplete

BOLD: int
EXTERNAL_STREAM: int
FAST_GLYPHS: int
FIXED_SIZES: int
FIXED_WIDTH: int
GLYPH_NAMES: int
HORIZONTAL: int
ITALIC: int
KERNING: int
KERNING_DEFAULT: int
KERNING_UNFITTED: int
KERNING_UNSCALED: int
LOAD_CROP_BITMAP: int
LOAD_DEFAULT: int
LOAD_FORCE_AUTOHINT: int
LOAD_IGNORE_GLOBAL_ADVANCE_WIDTH: int
LOAD_IGNORE_TRANSFORM: int
LOAD_LINEAR_DESIGN: int
LOAD_MONOCHROME: int
LOAD_NO_AUTOHINT: int
LOAD_NO_BITMAP: int
LOAD_NO_HINTING: int
LOAD_NO_RECURSE: int
LOAD_NO_SCALE: int
LOAD_PEDANTIC: int
LOAD_RENDER: int
LOAD_TARGET_LCD: int
LOAD_TARGET_LCD_V: int
LOAD_TARGET_LIGHT: int
LOAD_TARGET_MONO: int
LOAD_TARGET_NORMAL: int
LOAD_VERTICAL_LAYOUT: int
MULTIPLE_MASTERS: int
SCALABLE: int
SFNT: int
VERTICAL: int
__freetype_build_type__: str
__freetype_version__: str

class FT2Font:
    ascender: Incomplete
    bbox: Incomplete
    descender: Incomplete
    face_flags: Incomplete
    family_name: Incomplete
    fname: Incomplete
    height: Incomplete
    max_advance_height: Incomplete
    max_advance_width: Incomplete
    num_charmaps: Incomplete
    num_faces: Incomplete
    num_fixed_sizes: Incomplete
    num_glyphs: Incomplete
    postscript_name: Incomplete
    scalable: Incomplete
    style_flags: Incomplete
    style_name: Incomplete
    underline_position: Incomplete
    underline_thickness: Incomplete
    units_per_EM: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def clear(self, *args, **kwargs): ...
    def draw_glyph_to_bitmap(self, *args, **kwargs): ...
    def draw_glyphs_to_bitmap(self, *args, **kwargs): ...
    def get_bitmap_offset(self, *args, **kwargs): ...
    def get_char_index(self, *args, **kwargs): ...
    def get_charmap(self, *args, **kwargs): ...
    def get_descent(self, *args, **kwargs): ...
    def get_glyph_name(self, *args, **kwargs): ...
    def get_image(self, *args, **kwargs): ...
    def get_kerning(self, *args, **kwargs): ...
    def get_name_index(self, *args, **kwargs): ...
    def get_num_glyphs(self, *args, **kwargs): ...
    def get_path(self, *args, **kwargs): ...
    def get_ps_font_info(self, *args, **kwargs): ...
    def get_sfnt(self, *args, **kwargs): ...
    def get_sfnt_table(self, *args, **kwargs): ...
    def get_width_height(self, *args, **kwargs): ...
    def get_xys(self, *args, **kwargs): ...
    def load_char(self, *args, **kwargs): ...
    def load_glyph(self, *args, **kwargs): ...
    def select_charmap(self, *args, **kwargs): ...
    def set_charmap(self, *args, **kwargs): ...
    def set_size(self, *args, **kwargs): ...
    def set_text(self, *args, **kwargs): ...
    def __buffer__(self, *args, **kwargs): ...

class FT2Image:
    def __init__(self, *args, **kwargs) -> None: ...
    def draw_rect(self, *args, **kwargs): ...
    def draw_rect_filled(self, *args, **kwargs): ...
    def __buffer__(self, *args, **kwargs): ...
