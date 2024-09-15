from docutils import nodes
from matplotlib import rcParamsDefault as rcParamsDefault

class _QueryReference(nodes.Inline, nodes.TextElement):
    def to_query_string(self): ...

def setup(app): ...
