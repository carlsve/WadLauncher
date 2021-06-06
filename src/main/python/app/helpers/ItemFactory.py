from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem

ID_ROLE = Qt.UserRole + 1
TYPE_ROLE = Qt.UserRole + 2

def make_generic(text, id):
    item = QStandardItem(text)
    item.setData(id, ID_ROLE)
    return item

def make_wad_item(data, flags=None, item=None):
    if not item:
        item = make_generic(data.name, data.id)
    item.setText(data.display_name)
    if flags:
        item.setFlags(flags)
    item.setData(data.id, ID_ROLE)
    item.setData(data.model_type, TYPE_ROLE)
    return item

def make_iwad_item(data):
    return make_generic(data.name, data.id)

def make_source_port_item(data):
    return make_generic(data.name, data.id)

def make_category_item(data, item=None):
    if not item:
        item = make_generic(data.name, data.id)
    item.setData(data.id, ID_ROLE)
    item.setText(data.display_name)
    item.setData(data.model_type, TYPE_ROLE)
    nameItemFont = item.font()
    nameItemFont.setBold(True)
    item.setFont(nameItemFont)
    return item

def make_pending_item(data, item=None):
    return make_generic('loading...', data.id)
