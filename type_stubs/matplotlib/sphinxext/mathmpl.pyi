from _typeshed import Incomplete
from docutils import nodes
from docutils.parsers.rst import Directive
from matplotlib import mathtext as mathtext
from matplotlib.rcsetup import validate_float_or_None as validate_float_or_None

class latex_math(nodes.General, nodes.Element): ...

def fontset_choice(arg): ...
def math_role(role, rawtext, text, lineno, inliner, options={}, content=[]): ...

class MathDirective(Directive):
    has_content: bool
    required_arguments: int
    optional_arguments: int
    final_argument_whitespace: bool
    option_spec: Incomplete
    def run(self): ...

def latex2png(
    latex, filename, fontset: str = "cm", fontsize: int = 10, dpi: int = 100
): ...
def latex2html(node, source): ...
def setup(app): ...
