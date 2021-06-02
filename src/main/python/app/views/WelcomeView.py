from PyQt5 import uic

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget

template_path = AppContext.Instance().get_resource('template/welcome.ui')
Form, Base = uic.loadUiType(template_path)

class WelcomeView(Base, Form):
    def __init__(self, root, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        add_widget(root, self, 'WELCOME')
