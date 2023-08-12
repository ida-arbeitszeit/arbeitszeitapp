from matplotlib._fontconfig_pattern import *
from _typeshed import Incomplete
from matplotlib._fontconfig_pattern import parse_fontconfig_pattern as parse_fontconfig_pattern
from pyparsing import ParseException

family_unescape: Incomplete
value_unescape: Incomplete
family_escape: Incomplete
value_escape: Incomplete

class FontconfigPatternParser:
    ParseException = ParseException
    def parse(self, pattern): ...
