from PyQt5.QtWidgets import QWidget, QListView, QAbstractItemView, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel

from app.helpers.StackedWidgetSelector import widget_changed, display_widget, WidgetIndices
from app.helpers.ItemFactory import make_wad_item, ID_ROLE
from app.helpers.ContextMenuFactory import make_context_menu

LIST_ITEM_FLAGS = Qt.ItemIsSelectable | Qt.ItemIsEnabled

class WadListView:
    def __init__(self, root, controller):
        self.controller = controller
        self.wads = controller.wads

        self.wadlist = root.findChild(QListView, 'wad_list')
        self.wadinfo = root.findChild(QWidget, 'wad_info')
        self.wadinfo.hide()
        self.selected_item = None

        self.wadlist_model = QStandardItemModel()
        for wad in self.wads.all():
            self.appendWad(wad)
        self.wadlist.setModel(self.wadlist_model)
        self.wadlist.setSelectionMode(QAbstractItemView.SingleSelection)
        self.wadlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.wadlist.selectionModel().selectionChanged.connect(self.select_item)
        self.wadlist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wadlist.customContextMenuRequested.connect(self.open_menu)
        widget_changed(root, self.on_widget_change)

        self.wadtable_button = root.findChild(QPushButton, 'sidebar_wadsview_table')
        def wadtable(): display_widget(root, WidgetIndices.WAD_TABLE)
        self.wadtable_button.clicked.connect(wadtable)

        self.wadtree = root.findChild(QPushButton, 'sidebar_wadsview_tree')
        def wadtable(): display_widget(root, WidgetIndices.WAD_TREE)
        self.wadtree.clicked.connect(wadtable)

    def on_widget_change(self, widget_index):
        if widget_index in [WidgetIndices.WAD_TABLE, WidgetIndices.WAD_TREE]:
            self.wadlist.hide()
            self.wadinfo.show()
        else:
            self.wadinfo.hide()
            self.wadlist.show()

    def open_menu(self, pos):
        if self.selected_item == None:
            return
        id = self.selected_item.data(ID_ROLE)
        wad = self.wads.find(id)

        wad_string = wad.display_name
        remove_wad_string = 'Remove ({})'.format(wad_string)
        def remove_wad():
            self.wadlist_model.removeRow(self.selected_item.row())
            self.controller.remove_wad(id)
        menu_actions = [(remove_wad_string, remove_wad)]

        execute_menu = make_context_menu(self.wadlist, menu_actions)
        execute_menu(pos)

    def select_item(self, selection):
        if len(selection.indexes()) == 0:
            self.selected_item = None
            return
        index = selection.indexes()[0]
        item = self.wadlist_model.itemFromIndex(index)
        self.selected_item = item

        self.wads.select_wad(item.data(ID_ROLE))

    def appendWad(self, wad):
        item = make_wad_item(wad, LIST_ITEM_FLAGS)
        self.wadlist_model.appendRow(item)

    def remove_item(self, wad):
        for row in range(self.wadlist_model.rowCount()):
            item = self.wadlist_model.item(row)
            if item and item.data(ID_ROLE) == wad.id:
                self.wadlist_model.removeRow(row)

    def import_wads(self, wads):
        for wad in wads:
            self.appendWad(wad)
