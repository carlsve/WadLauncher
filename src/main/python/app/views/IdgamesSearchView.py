from PyQt5 import uic
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget
from app.views.widgets.SearchResultWidget import SearchResultWidget
from app.views.widgets.SearchBar import SearchBar

template_path = AppContext.Instance().get_resource('template/idgames_search.ui')
Form, Base = uic.loadUiType(template_path)

class IdgamesSearchView(Base, Form):
    def __init__(self, root, controller, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        add_widget(root, self, 'IDGAMES_SEARCH')

        self.searchbar = SearchBar(root, controller)
        self.controller = controller

        self.search_results_container = self.findChild(QScrollArea, 'idgames_search_results_container')
        self.search_results_container.setWidgetResizable(True)
        self.search_results = self.findChild(QWidget, 'idgames_search_results')

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(9, 9, 9, 9)
        self.layout.setAlignment(Qt.AlignTop)
        self.search_results.setLayout(self.layout)

        self.layout.addWidget(QLabel('Search result will show here...'))

        self.search_results_widgets = {}

    def updateResults(self, result):
        for i in reversed(range(self.layout.count())): 
            widgetToRemove = self.layout.itemAt(i).widget()
            # remove it from the layout list
            self.layout.removeWidget(widgetToRemove)
            # remove it from the gui
            if widgetToRemove != None:
                widgetToRemove.setParent(None)

        search_result = result[0].get('file', [])
        if type(search_result) != list:
            search_result = [search_result]

        warning = result[0].get('warning', None)
        if warning:
            self.layout.addWidget(QLabel(warning['type']))
            self.layout.addWidget(QLabel(warning['message']))

        self.search_results_widgets = {}
        for item in search_result:
            search_result_widget = SearchResultWidget(self.controller)
            search_result_widget.set_data(item)
            self.layout.addWidget(search_result_widget)
            self.search_results_widgets[item['id']] = search_result_widget
        
        self.layout.addStretch()
