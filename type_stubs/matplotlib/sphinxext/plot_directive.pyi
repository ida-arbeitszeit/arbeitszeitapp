from _typeshed import Incomplete
from docutils.parsers.rst import Directive
from matplotlib import cbook as cbook
from matplotlib.backend_bases import FigureManagerBase as FigureManagerBase

__version__: int

def mark_plot_labels(app, document) -> None: ...

class PlotDirective(Directive):
    has_content: bool
    required_arguments: int
    optional_arguments: int
    final_argument_whitespace: bool
    option_spec: Incomplete
    def run(self): ...

def setup(app): ...
def contains_doctest(text): ...

TEMPLATE_SRCSET: Incomplete
TEMPLATE: Incomplete
exception_template: str
plot_context: Incomplete

class ImageFile:
    basename: Incomplete
    dirname: Incomplete
    formats: Incomplete
    def __init__(self, basename, dirname) -> None: ...
    def filename(self, format): ...
    def filenames(self): ...

def out_of_date(original, derived, includes: Incomplete | None = None): ...

class PlotError(RuntimeError): ...

def clear_state(plot_rcparams, close: bool = True) -> None: ...
def get_plot_formats(config): ...
def render_figures(
    code,
    code_path,
    output_dir,
    output_base,
    context,
    function_name,
    config,
    context_reset: bool = False,
    close_figs: bool = False,
    code_includes: Incomplete | None = None,
): ...
def run(arguments, content, options, state_machine, state, lineno): ...
