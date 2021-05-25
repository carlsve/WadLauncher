from PyQt5 import uic
from PyQt5.QtWidgets import QTreeView, QAbstractItemView
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from app.AppContext import AppContext
from app.helpers.StackedWidgetSelector import add_widget
from app.helpers.ContextMenuFactory import make_context_menu
from app.helpers.WadItemFactory import make_wad_item, DATA_ROLE
from app.views.widgets.promoted.DeselectableTreeView import DeselectableTreeView

template_path = AppContext.Instance().get_resource('template/wadtree.ui')
Form, Base = uic.loadUiType(template_path)

TREE_WAD_FLAGS = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemNeverHasChildren
ID_ROLE = Qt.UserRole + 1
TYPE_ROLE = Qt.UserRole + 2

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
        self.temp_move_storage = { 'from': None, 'to': None }


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
            to_item.appendRow(take_from)
            self.categories.add_child(to_item.data(ID_ROLE), from_item.data(ID_ROLE))
        elif indicator == QAbstractItemView.AboveItem:
            to_parent.insertRow(to_row + adjust[indicator], take_from)
            self.categories.insert_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE), to_row + adjust[indicator])
        elif indicator == QAbstractItemView.BelowItem:
            to_parent.insertRow(to_row + adjust[indicator], take_from)
            self.categories.insert_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE), to_row + adjust[indicator])
        elif indicator == QAbstractItemView.OnViewport:
            to_parent.appendRow(take_from)
            self.categories.add_child(to_parent.data(ID_ROLE), from_item.data(ID_ROLE))

        self.categories.save()

    def change_category_text(self, item):
        if all(self.finished_loading.values()):
            item_text = item.text()
            if item.data(TYPE_ROLE) == 'categories' and self.categories.find(item.data(ID_ROLE))['name'] != item_text:
                self.controller.edit_category(item.data(ID_ROLE), name=item_text)

    def select_tree_index(self, selection):
        if len(selection.indexes()) == 0:
            return
        index = selection.indexes()[0]
        item = self.wadtree_model.itemFromIndex(index)
        if item.data(TYPE_ROLE) == 'wads':
            self.wads.select_wad(item.data(ID_ROLE))

    def remove_wad(self, item):
        parent = item.parent() or self.root
        self.categories.remove_child(parent.data(ID_ROLE), item.data(ID_ROLE))
        self.categories.save()
        self.wads.remove(item.data(ID_ROLE))

    def wad_removed(self, data):
        item = self.id_item_mapping[data['id']]
        parent = item.parent() or self.root
        parent.removeRow(item.row())

    def new_category(self, index):
        item = self.wadtree_model.itemFromIndex(index) or self.root
        if item.data(TYPE_ROLE) == 'wads':
            item = self.wadtree_model.itemFromIndex(index.parent()) or self.root
        self.categories.new(item.data(ID_ROLE))

    def category_added(self, parent_id, data):
        item = self.make_tree_item(data['name'], data)
        nameItemFont = item.font()
        nameItemFont.setBold(True)
        item.setFont(nameItemFont)
        self.id_item_mapping[parent_id].appendRow(item)

    def remove_category(self, id):
        parent = self.id_item_mapping[id].parent() or self.root
        self.categories.remove(id, parent.data(ID_ROLE))

    def category_removed(self, parent_id, id):
        parent = self.id_item_mapping[parent_id]
        item = self.id_item_mapping.pop(id)
        item_row = item.row()
        for row in range(item.rowCount()):
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
                self.remove_category(data['id'])
            entries_by_model = {
                'categories': ('Remove category ({})'.format(data.get('name')), remove_category),
                'wads': ('Remove ({})'.format(data.get('title') or data.get('name')), remove_wad)
            }
            entries.append(entries_by_model[item.data(TYPE_ROLE).lower()])

        execute_menu = make_context_menu(self, entries)
        execute_menu(pos)

    def appendWad(self, data):
        if data['id'] in self.pending_children:
            item = self.pending_children.pop(data['id'])
            item.setText(data['name'])
            item.setData(data['model_type'], TYPE_ROLE)
            item.setFlags(TREE_WAD_FLAGS)
            self.id_item_mapping[data['id']] = item
        else:
            self.loaded_wads[data['id']] = data

    def appendCategory(self, data):
        is_root = data.get('is_root', 'False') == 'True'
        item = None
        if is_root:
            item = self.root
            item.setData(data['id'], ID_ROLE)
            item.setData(data['model_type'], TYPE_ROLE)
        elif data['id'] in self.pending_children:
            item = self.pending_children.pop(data['id'])
            item.setText(data['name'])
            item.setData(data['model_type'], TYPE_ROLE)
        else:
            item = self.make_tree_item(data['name'], data)
            self.loaded_categories[data['id']] = item

        self.id_item_mapping[data['id']] = item
        if not is_root:
            nameItemFont = item.font()
            nameItemFont.setBold(True)
            item.setFont(nameItemFont)

        for child_id in data['children']:
            child_item = None
            if child_id in self.loaded_wads:
                wad = self.loaded_wads.pop(child_id)
                child_item = self.make_tree_item(wad['name'], wad)
                child_item.setFlags(TREE_WAD_FLAGS)
                self.id_item_mapping[data['id']] = item
            elif child_id in self.loaded_categories:
                child_item = self.loaded_categories.pop(child_id)
            else:
                child_item = QStandardItem('loading... ')
                child_item.setData(child_id, ID_ROLE)
                self.pending_children[child_id] = child_item
            item.appendRow(child_item)

    def finish_loading(self, model_type):
        self.finished_loading[model_type] = True
        if not all(self.finished_loading.values()): return
        wads_missing_categories = False
        root_id = self.root.data(ID_ROLE)
        for wad in self.loaded_wads.values():
            if wad['id'] in self.pending_children:
                item = self.pending_children.pop(wad['id'])
                item.setText(wad['name'])
                item.setData(wad['model_type'], TYPE_ROLE)
                item.setFlags(TREE_WAD_FLAGS)
                self.id_item_mapping[wad['id']] = item
            else:
                item = self.make_tree_item(wad['name'], wad)
                self.root.appendRow(item)
                wads_missing_categories = True
                self.categories.add_child(root_id, wad['id'])
                self.id_item_mapping[wad['id']] = item
        for category in self.loaded_categories.values():
            self.root.appendRow(category)
            wads_missing_categories = True
            self.categories.add_child(root_id, category.data(ID_ROLE))
        if wads_missing_categories:
            self.categories.save()

        for pending_child in self.pending_children.values():
            parent_id = (pending_child.parent() or self.root).data(ID_ROLE)
            self.categories.remove_child(parent_id, pending_child.data(ID_ROLE))
            self.categories.save()

    def make_tree_item(self, text, data):
        item = QStandardItem(text)
        item.setData(data['id'], ID_ROLE)
        item.setData(data['model_type'], TYPE_ROLE)
        self.id_item_mapping[data['id']] = item
        return item
