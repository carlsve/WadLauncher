from PyQt5 import uic
from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from dataclasses import dataclass

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget
from app.helpers.ContextMenuFactory import make_context_menu
from app.helpers.ItemFactory import make_wad_item, make_pending_item, make_category_item, ID_ROLE, TYPE_ROLE

template_path = AppContext.Instance().get_resource('template/wadtree.ui')
Form, Base = uic.loadUiType(template_path)

TREE_WAD_FLAGS = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemNeverHasChildren

@dataclass
class Pending:
    id: str
    model_type: str = 'pending'

class WadTreeView(Base, Form):
    def __init__(self, root, controller, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setupUi(self)
        add_widget(root, self, 'WAD_TREE')

        self.wads = controller.models.wads
        self.categories = controller.models.categories
        self.controller = controller
        self.loaded_wads = {}
        self.loaded_categories = {}
        self.pending_children = {}
        self.finished_loading = { 'categories': False, 'wads': False }
        self.id_item_mapping = {}

        self.wadtree = self.findChild(QTreeView, 'wadtree')
        self.wadtree.dropEvent = self.dropEvent
        self.wadtree.setDragEnabled(True)
        self.wadtree.viewport().setAcceptDrops(True)
        self.wadtree.setDropIndicatorShown(True)
        self.wadtree.setDragDropMode(QAbstractItemView.DragDrop)
        self.wadtree.setDefaultDropAction(Qt.MoveAction)
        self.wadtree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.wadtree.customContextMenuRequested.connect(self.open_menu)

        self.wadtree_model = QStandardItemModel()
        self.wadtree.setModel(self.wadtree_model)

        self.wadtree.selectionModel().selectionChanged.connect(self.select_tree_index)
        self.wadtree_model.itemChanged.connect(self.change_category_text)

        self.root = self.wadtree_model.invisibleRootItem()

    def dropEvent(self, e):
        from_index = e.source().currentIndex()
        from_item = self.wadtree_model.itemFromIndex(from_index)
        from_parent = from_item.parent() or self.root
        from_row = from_item.row()

        to_index = self.wadtree.indexAt(e.pos())
        to_item = self.wadtree_model.itemFromIndex(to_index) or self.root
        to_parent = to_item.parent() or self.root
        to_row = to_item.row()

        take_from = from_parent.takeRow(from_row)
        sharing_parents = from_parent == to_parent
        adjust = {
            QAbstractItemView.AboveItem: (-1) if sharing_parents and from_row < to_row else 0,
            QAbstractItemView.BelowItem: (0) if sharing_parents and from_row < to_row else 1
        }
        self.categories.remove_child(from_parent.data(ID_ROLE), from_item.data(ID_ROLE))

        indicator = self.wadtree.dropIndicatorPosition()
        if indicator == QAbstractItemView.OnItem:
            self.categories.add_child(to_item.data(ID_ROLE), from_item.data(ID_ROLE))
            to_item.appendRow(take_from)
        elif indicator == QAbstractItemView.AboveItem:
            self.categories.insert_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE), to_row + adjust[indicator])
            to_parent.insertRow(to_row + adjust[indicator], take_from)
        elif indicator == QAbstractItemView.BelowItem:
            self.categories.insert_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE), to_row + adjust[indicator])
            to_parent.insertRow(to_row + adjust[indicator], take_from)
        elif indicator == QAbstractItemView.OnViewport:
            self.categories.add_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE))
            to_parent.appendRow(take_from)

        self.categories.save()

    def change_category_text(self, item):
        if all(self.finished_loading.values()):
            item_text = item.text()
            if item.data(TYPE_ROLE) == 'categories' and self.categories.find(item.data(ID_ROLE)).name != item_text:
                self.controller.edit_category(item.data(ID_ROLE), name=item_text)

    def select_tree_index(self, selection):
        if len(selection.indexes()) == 0:
            return
        index = selection.indexes()[0]
        item = self.wadtree_model.itemFromIndex(index)
        if item.data(TYPE_ROLE) == 'wads':
            self.wads.select_wad(item.data(ID_ROLE))

    def remove_wad(self, item):
        self.wads.remove(item.data(ID_ROLE))

    def wad_removed(self, data):
        item = self.id_item_mapping[data.id]
        parent = item.parent() or self.root
        self.categories.remove_child(parent.data(ID_ROLE), item.data(ID_ROLE))
        parent.removeRow(item.row())
        self.categories.save()
    
    def import_wad(self, id, parent_name):
        data = self.wads.find(id)
        item = self.make_tree_item(data)
        parent = self.categories.find_by(name=parent_name)
        parent_item = None
        if not parent:
            parent_id = self.categories.create(name=parent_name, children=[])
            parent_item = self.make_tree_item(self.categories.find(parent_id))
            self.root.appendRow(parent_item)
            self.categories.add_child(self.root.data(ID_ROLE), parent_item.data(ID_ROLE))
        else:
            parent_item = self.id_item_mapping[parent.id]
        index = self.wadtree_model.indexFromItem(parent_item)
        self.wadtree.expand(index)
        self.categories.add_child(parent_item.data(ID_ROLE), data.id)
        parent_item.appendRow(item)
        self.categories.save()

    def new_category(self, index):
        item = self.wadtree_model.itemFromIndex(index) or self.root
        if item.data(TYPE_ROLE) == 'wads':
            item = self.wadtree_model.itemFromIndex(index.parent()) or self.root
        self.categories.new(item.data(ID_ROLE))

    def category_added(self, parent_id, data):
        item = self.make_tree_item(data)
        self.id_item_mapping[parent_id].appendRow(item)

    def remove_category(self, id):
        parent = self.id_item_mapping[id].parent() or self.root
        self.categories.remove(id, parent.data(ID_ROLE))

    def category_removed(self, parent_id, id):
        parent = self.id_item_mapping[parent_id]
        item = self.id_item_mapping.pop(id)
        item_row = item.row()
        for row in reversed(range(item.rowCount())):
            child = item.takeChild(row)
            parent.insertRow(item_row + 1, child)
        parent.removeRow(item_row)

    def open_menu(self, pos):
        index = self.wadtree.indexAt(pos)
        entries = [('Add Category', lambda *_: self.new_category(index))]

        if index.isValid():
            item = self.wadtree_model.itemFromIndex(index)
            model = getattr(self, item.data(TYPE_ROLE).lower())
            data = model.find(item.data(ID_ROLE))

            def remove_wad():
                self.remove_wad(item)
            def remove_category():
                self.remove_category(data.id)
            entries_by_model = {
                'categories': ('Remove category ({})'.format(data.name), remove_category),
                'wads': ('Remove ({})'.format(data.display_name), remove_wad)
            }
            entries.append(entries_by_model[item.data(TYPE_ROLE).lower()])

        execute_menu = make_context_menu(self, entries)
        execute_menu(pos)

    def appendWad(self, data):
        if data.id in self.pending_children:
            from_item = self.pending_children.pop(data.id)
            item = self.make_tree_item(data, from_item=from_item)
        else:
            self.loaded_wads[data.id] = data

    def appendCategory(self, data):
        is_root = data.is_root
        item = None
        if is_root:
            item = self.make_tree_item(data, self.root)
            self.root = item
        elif data.id in self.pending_children:
            from_item = self.pending_children.pop(data.id)
            item = self.make_tree_item(data, from_item=from_item)
        else:
            item = self.make_tree_item(data)
            self.loaded_categories[data.id] = item

        for child_id in data.children:
            child_item = None
            if child_id in self.loaded_wads:
                wad = self.loaded_wads.pop(child_id)
                child_item = self.make_tree_item(wad)
                child_item.setFlags(TREE_WAD_FLAGS)
            elif child_id in self.loaded_categories:
                child_item = self.loaded_categories.pop(child_id)
            else:
                child_item = self.make_tree_item(Pending(id=child_id))
                self.pending_children[child_id] = child_item
            item.appendRow(child_item)

        if data.id not in self.loaded_categories:
            index = self.wadtree_model.indexFromItem(item)
            self.wadtree.expand(index)

    def finish_loading(self, model_type):
        self.finished_loading[model_type] = True
        if not all(self.finished_loading.values()): return
        wads_missing_categories = False
        root_id = self.root.data(ID_ROLE)
        root_category = self.categories.find(root_id)
        for wad in self.loaded_wads.values():
            if wad.id in self.pending_children:
                item = self.pending_children.pop(wad.id)
                self.make_tree_item(wad, from_item=item)
            else:
                item = self.make_tree_item(wad)
                root_category.add_child(wad.id)
                self.root.appendRow(item)
                wads_missing_categories = True
        for category in self.loaded_categories.values():
            root_category.add_child(category.id)
            self.root.appendRow(category)
            wads_missing_categories = True
        if wads_missing_categories:
            self.categories.save()

        for pending_child in self.pending_children.values():
            parent = (pending_child.parent() or self.root)
            parent_category = self.categories.find(parent.data(ID_ROLE))
            parent_category.remove_child(pending_child.data(ID_ROLE))
            parent.removeRow(pending_child.row())
            self.categories.save()

    def make_tree_item(self, data, from_item=None):
        item_type = data.model_type
        make_item = {
            'categories': make_category_item,
            'wads': lambda data, item: make_wad_item(data, TREE_WAD_FLAGS, item),
            'pending': make_pending_item
        }
        item = make_item[item_type](data, from_item)
        self.id_item_mapping[data.id] = item

        return item
