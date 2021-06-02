from PyQt5 import uic
from PyQt5.QtWidgets import QTableView, QLineEdit, QAbstractItemView
from PyQt5.QtCore import Qt, QModelIndex, QItemSelectionModel, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget
from app.helpers.ItemFactory import make_wad_item, ID_ROLE
from app.helpers.ContextMenuFactory import make_context_menu

template_path = AppContext.Instance().get_resource('template/wadtable.ui')
Form, Base = uic.loadUiType(template_path)

TABLE_ITEM_FLAGS = Qt.ItemIsSelectable | Qt.ItemIsEnabled

class WadTableSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setFilterCaseSensitivity(False)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        num_columns = model.columnCount()

        def get_index(i): return model.index(source_row, i, source_parent)
        def get_header(i): return model.headerData(i, Qt.Horizontal).lower()
        def get_row(i): return model.data(get_index(i))
        model_data = dict([[get_header(i), get_row(i)] for i in range(num_columns)])
        
        filter_str = self.filterRegExp().pattern()
        filter_data = {}
        for elem in filter_str.split(','):
            try:
                key, val = elem.split(':')
                filter_data[key.strip()] = val.strip()
            except ValueError:
                pass
        for key in model_data:
            if key in filter_data:
                if filter_data[key].lower() not in model_data[key].lower():
                    return False

        return True

class WadTableView(Base, Form):
    def __init__(self, root, controller, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        add_widget(root, self, 'WAD_TABLE')

        self.wads = controller.wads
        self.controller = controller

        self.proxy = WadTableSortFilterProxyModel(root)
        self.wadtable_model = QStandardItemModel()
        self.proxy.setSourceModel(self.wadtable_model)
        self.selected_item = None

        self.wadtable = self.findChild(QTableView, 'wadtable')
        self.wadtable.setModel(self.proxy)
        self.wadtable.selectionModel().selectionChanged.connect(self.select_item)
        self.wadtable.setSortingEnabled(True)
        self.wadtable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wadtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.wadtable.customContextMenuRequested.connect(self.open_menu)

        self.wadtable_filter = self.findChild(QLineEdit, 'wadtable_filter')
        self.wadtable_filter.textChanged.connect(self.proxy.setFilterFixedString)

        self.keys = ['title', 'filename', 'author', 'date', 'rating']
        self.wadtable_model.setHorizontalHeaderLabels([key.capitalize() for key in self.keys])

        for wad in self.wads.all():
            self.appendRow(wad)

    def open_menu(self, pos):
        if self.selected_item == None:
            return
        id = self.selected_item.data(ID_ROLE)
        wad = self.wads.find(id)

        wad_string = wad.display_name()
        remove_wad_string = 'Remove ({})'.format(wad_string)
        def remove_wad():
            self.wadtable_model.removeRow(self.selected_item.row())
            self.controller.remove_wad(id)
        menu_actions = [(remove_wad_string, remove_wad)]

        execute_menu = make_context_menu(self.wadtable, menu_actions)
        execute_menu(pos)

    def select_item(self, selection):
        if len(selection.indexes()) == 0:
            self.selected_item = None
            return

        proxy_index = selection.indexes()[0]
        index = self.proxy.mapToSource(proxy_index)
        item = self.wadtable_model.itemFromIndex(index)

        self.selected_item = item
        self.wads.select_wad(item.data(ID_ROLE))

    def appendRow(self, wad):
        item = make_wad_item(wad, TABLE_ITEM_FLAGS)
        def make_column_item(wad, key):
            return QStandardItem(getattr(wad, key) or 'unknown')
        column_items = [make_column_item(wad, key) for key in self.keys[1:]]
        items = [item, *column_items]

        self.wadtable_model.appendRow(items)

    def remove_item(self, wad):
        for row in range(self.wadtable_model.rowCount()):
            item = self.wadtable_model.item(row)
            if item and item.data(ID_ROLE) == wad.id:
                self.wadtable_model.removeRow(row)