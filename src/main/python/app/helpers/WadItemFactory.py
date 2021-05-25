from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem

ID_ROLE = Qt.UserRole + 1
TYPE_ROLE = Qt.UserRole + 2

def make_wad_item(wad, flags):
    string = wad.get('title') or wad.get('name')

    item = QStandardItem(string)
    item.setFlags(flags)
    item.setData(wad['id'], ID_ROLE)
    return item
