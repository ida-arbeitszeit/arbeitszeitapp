from _typeshed import Incomplete
from matplotlib.backends.qt_compat import QtCore as QtCore
from matplotlib.backends.qt_compat import QtGui as QtGui
from matplotlib.backends.qt_compat import QtWidgets as QtWidgets

__version__: str
BLACKLIST: Incomplete

class ColorButton(QtWidgets.QPushButton):
    colorChanged: Incomplete
    def __init__(self, parent: Incomplete | None = None) -> None: ...
    def choose_color(self) -> None: ...
    def get_color(self): ...
    def set_color(self, color) -> None: ...
    color: Incomplete

def to_qcolor(color): ...

class ColorLayout(QtWidgets.QHBoxLayout):
    lineedit: Incomplete
    colorbtn: Incomplete
    def __init__(self, color, parent: Incomplete | None = None) -> None: ...
    def update_color(self) -> None: ...
    def update_text(self, color) -> None: ...
    def text(self): ...

def font_is_installed(font): ...
def tuple_to_qfont(tup): ...
def qfont_to_tuple(font): ...

class FontLayout(QtWidgets.QGridLayout):
    family: Incomplete
    size: Incomplete
    italic: Incomplete
    bold: Incomplete
    def __init__(self, value, parent: Incomplete | None = None) -> None: ...
    def get_font(self): ...

def is_edit_valid(edit): ...

class FormWidget(QtWidgets.QWidget):
    update_buttons: Incomplete
    data: Incomplete
    widgets: Incomplete
    formlayout: Incomplete
    def __init__(
        self,
        data,
        comment: str = "",
        with_margin: bool = False,
        parent: Incomplete | None = None,
    ) -> None: ...
    def get_dialog(self): ...
    def setup(self): ...
    def get(self): ...

class FormComboWidget(QtWidgets.QWidget):
    update_buttons: Incomplete
    combobox: Incomplete
    stackwidget: Incomplete
    widgetlist: Incomplete
    def __init__(
        self, datalist, comment: str = "", parent: Incomplete | None = None
    ) -> None: ...
    def setup(self) -> None: ...
    def get(self): ...

class FormTabWidget(QtWidgets.QWidget):
    update_buttons: Incomplete
    tabwidget: Incomplete
    widgetlist: Incomplete
    def __init__(
        self, datalist, comment: str = "", parent: Incomplete | None = None
    ) -> None: ...
    def setup(self) -> None: ...
    def get(self): ...

class FormDialog(QtWidgets.QDialog):
    apply_callback: Incomplete
    formwidget: Incomplete
    float_fields: Incomplete
    bbox: Incomplete
    def __init__(
        self,
        data,
        title: str = "",
        comment: str = "",
        icon: Incomplete | None = None,
        parent: Incomplete | None = None,
        apply: Incomplete | None = None,
    ) -> None: ...
    def register_float_field(self, field) -> None: ...
    def update_buttons(self) -> None: ...
    data: Incomplete
    def accept(self) -> None: ...
    def reject(self) -> None: ...
    def apply(self) -> None: ...
    def get(self): ...

def fedit(
    data,
    title: str = "",
    comment: str = "",
    icon: Incomplete | None = None,
    parent: Incomplete | None = None,
    apply: Incomplete | None = None,
) -> None: ...
