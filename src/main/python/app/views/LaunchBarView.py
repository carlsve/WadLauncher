import os

from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

ID_ROLE = Qt.UserRole + 1

class LaunchBarView:
    def __init__(self, root, controller):
        root = root.findChild(QWidget, 'launchbar')
        self.controller = controller

        self.selected_wad_name = root.findChild(QLabel, 'launchbar_selected_wad')
        self.selected_wad_name.setText('No wad selected')

        self.iwad_selector_model = QStandardItemModel()
        for iwad in controller.models.iwads.all():
            self.append_iwad(iwad)
        self.iwad_selector = root.findChild(QComboBox, 'launchbar_iwad_selector')
        self.iwad_selector.setModel(self.iwad_selector_model)
        self.iwad_selector.currentIndexChanged.connect(self.select_iwad)

        self.source_port_selector_model = QStandardItemModel()
        for source_port in controller.models.source_ports.all():
            self.append_source_port(source_port)

        self.source_port_selector = root.findChild(QComboBox, 'launchbar_source_port_selector')
        self.source_port_selector.setModel(self.source_port_selector_model)
        self.source_port_selector.currentIndexChanged.connect(self.select_source_port)

        launch_wad_button = root.findChild(QPushButton, 'launchbar_launch_button')
        launch_wad_button.clicked.connect(self.controller.launch_wad_press)

    def append_iwad(self, iwad):
        item = QStandardItem(iwad['name'])
        item.setData(iwad['id'], ID_ROLE)
        self.iwad_selector_model.appendRow(item)
    
    def select_iwad(self, index):
        item = self.iwad_selector_model.item(index)
        self.controller.select_iwad(item.data(ID_ROLE))

    def append_source_port(self, source_port):
        item = QStandardItem(source_port['name'])
        item.setData(source_port['id'], ID_ROLE)
        self.source_port_selector_model.appendRow(item)
    
    def select_source_port(self, index):
        item = self.source_port_selector_model.item(index)
        self.controller.select_source_port(item.data(ID_ROLE))

    def update_selected_wad(self, wad):
        if wad == None:
            self.selected_wad_name.setText('No wad selected')
        else:
            self.selected_wad_name.setText((wad.get('title') or wad['name']) + ' ({})'.format(os.path.basename(wad['file_path'])))
