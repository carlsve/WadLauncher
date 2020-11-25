import enum

from PyQt5.QtWidgets import QStackedWidget

class WidgetIndices(enum.Enum):
    IDGAMES_SEARCH = 0
    IDGAMES_DETAIL = 1
    WELCOME = 2

def display_widget(root, widget_index):
    stackedWidget = root.findChild(QStackedWidget, 'main_stack')
    stackedWidget.setCurrentIndex(widget_index.value)